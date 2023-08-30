from datetime import datetime
import os
import threading
import cv2
import psycopg2 
import torch
from ultralytics import YOLO
import subprocess
import time

def detection_worker(model,frame):
    
    results = model.track(frame, persist=True)
    for result in results:       
        if result:
            now = datetime.now()
            formatted_date = now.strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
            name_image = f'{formatted_date}.jpg'
            link_img = os.path.join('images', name_image) 
            cv2.imwrite(link_img, frame)     #conf
            
            # Преобразование данных
            array_boxes_xywh = result.boxes.xywh.to('cpu').tolist() 
            result_array_boxes_xywh = []
            for sublist in array_boxes_xywh:
                result_array_boxes_xywh.extend(sublist)
            array_boxes_conf = result.boxes.conf.to('cpu').tolist() # Вероятность
            array_boxes_label = result.boxes.cls.to('cpu').tolist() # Класс объекта
            array_id_name = result.boxes.id.int().to('cpu').tolist()

            # Передаем данные в процедуру
            connection = psycopg2.connect(user="postgres", #conf
                            password="postgres", #conf
                            host="localhost", #conf
                            port="5433", #conf 
                            database="grant_composition") #conf
            cursor = connection.cursor()
            args = [result_array_boxes_xywh, array_boxes_conf, link_img, array_id_name,array_boxes_label] # 
            cursor.callproc('insert_data', args)
            connection.commit()
            cursor.close()
    pass

def main(camera_ip):
    source = 'rtsp://root:admin@' + camera_ip + '/axis-media/media.amp' #conf
    model = YOLO("yolov8l.pt") #conf 
    
    cap = cv2.VideoCapture(source)
    while cap.isOpened():
        try:
            ret, frame = cap.read()
            if not ret:
                break
            print('кадр')
            if threading.active_count() < 2:  # Учтем главный поток и два дополнительных
                threading.Thread(target=detection_worker, args=(model,frame), name=str('detection_worker')).start()
        except cv2.error as e:
            print(f'CV2 Exception: {str(e)}')
    cap.release()
    


def find_camera_ip(camera_name):
    # Выполняем ping по названию
    try:
        response = subprocess.call(['ping', '-c', '1', '-W', '1', camera_name])
        if response == 0: # если 0 то ответ получен
            for line in subprocess.check_output(['ping', '-c', '1', '-W', '1', camera_name]).decode('utf-8').split('\n'):
                i = 0
                for word in line.split(' '): 
                    if i == 2:
                        return word[1:-1]
                    i+=1
        return None
    except subprocess.CalledProcessError:
        response = subprocess.call(['systemd-resolve', '--flush-caches'])
        return None

if __name__ == "__main__":
    while True: # бесконечный цикл для пинга
        camera_name = "axis-b8a44f0899b0"
        # camera_ip = '10.10.132.21'
        # print(torch.cuda.is_available())
        # main(camera_ip)
        
        camera_ip = find_camera_ip(camera_name)
        if camera_ip:
            print(f"IP-адрес камеры {camera_name}: {camera_ip}")
            main(camera_ip)
            print('связь прервана')
        else:
            print(f"Камера {camera_name} не найдена.")
        time.sleep(3)
