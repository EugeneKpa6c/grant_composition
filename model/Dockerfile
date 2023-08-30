# FROM nvidia/cuda:12.2.0-devel-ubuntu20.04
FROM ubuntu:20.04

# соращаем установку
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# добавляем все катологи для скачивания
COPY pip.conf pip.conf
ENV PIP_CONFIG_FILE pip.conf

RUN apt update
RUN apt install curl -y
RUN apt-get update --fix-missing && apt-get install -y python3 python3-pip

# копируем списка библиотек requirements.txt
COPY requirements.txt .

# обновляем pip и устанавливаем библиотеки

RUN pip3 install --upgrade pip 
RUN pip3 install -r requirements.txt
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# чтобы работала камера
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    iputils-ping 
# добавляем сам файл для запуска программы
COPY grant_composition_stream.py grant_composition_stream.py
COPY yolov8l.pt yolov8l.pt

CMD ["python3", "/app/detection_stream.py"]
# # чтобы о постоянно работал
# RUN echo 'ping localhost &' > /bootstrap.sh
# RUN echo 'sleep infinity' >> /bootstrap.sh
# RUN chmod +x /bootstrap.sh

# CMD /bootstrap.sh
#docker build -t model_detection .

#-d --image-name my-remote-container-registry/cuda --cuda-version 12.2.0 --os ubuntu --os-version 20.04 --arch x86_64,arm64 --push