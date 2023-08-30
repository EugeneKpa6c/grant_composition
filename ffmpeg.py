import subprocess
import os

def get_ffmpeg_path():
    platform = os.sys.platform
    if platform == "win32":
        find_command = "where"
    else:
        find_command = "which"
    
    try:
        ffmpeg_path = subprocess.check_output([find_command, "ffmpeg"]).decode().strip()
    except subprocess.CalledProcessError:
        raise Exception("ffmpeg not found in system path.")
    
    return ffmpeg_path

def run_ffmpeg(rtsp_url, output_path):
    ffmpeg_path = get_ffmpeg_path()
    command = [
        ffmpeg_path,
        '-i', rtsp_url,
        '-c:v', 'copy',
        '-c:a', 'aac',  # Конвертируем аудио в формат AAC для DASH
        '-strict', '-2',
        '-f', 'dash',
        '-window_size', '5',  # Опционально: количество последних сегментов, которые сохраняются в списке
        '-remove_at_exit', '1',  # Удаление сегментов при завершении работы
        output_path
    ]
    
    # Start ffmpeg in the background
    process = subprocess.Popen(command)

if __name__ == "__main__":
    rtsp_url = "rtsp://root:admin@10.10.132.21/axis-media/media.amp"
    output_path = "assets/output.mpd"  # DASH манифест
    run_ffmpeg(rtsp_url, output_path)
