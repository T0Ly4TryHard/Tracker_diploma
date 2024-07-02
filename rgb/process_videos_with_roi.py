import os
import cv2
from videoprocess_vit2 import VideoProcessor

def read_roi_file(roi_file_path):
    with open(roi_file_path, 'r') as f:
        line = f.readline().strip()
        # Пример строки: "ROI coordinates: x=100, y=150, w=200, h=250"
        parts = line.split(',')
        roi = [int(part.split('=')[1]) for part in parts]
        return roi

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.mov')):
                video_path = os.path.join(root, file)
                roi_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}_roi.txt")

                if os.path.exists(roi_file_path):
                    roi = read_roi_file(roi_file_path)
                    processor = VideoProcessor(video_path, roi)
                    processor.process()
                else:
                    print(f"Файл ROI не найден для видео {video_path}")

if __name__ == "__main__":
    directory = "./data"
    process_directory(directory)