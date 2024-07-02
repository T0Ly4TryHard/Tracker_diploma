import os
import cv2

def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл {video_path}")
        return
    
    ret, frame = cap.read()
    if not ret:
        print(f"Не удалось прочитать кадр из видеофайла {video_path}")
        return
    
    display_name = "Video"
    cv2.putText(frame, 'Select target ROI and press ENTER', (20, 30), 
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (0, 0, 0), 1)
    cv2.imshow(display_name, frame)
    
    x, y, w, h = cv2.selectROI(display_name, frame, fromCenter=False)
    cv2.destroyWindow(display_name)
    
    init_state = [x, y, w, h]
    
    with open(output_path, 'w') as f:
        f.write(f"ROI coordinates: x={x}, y={y}, w={w}, h={h}\n")
    
    cap.release()
    print(f"Координаты ROI сохранены в {output_path}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.mov')):
                video_path = os.path.join(root, file)
                output_path = os.path.join(root, f"{os.path.splitext(file)[0]}_roi.txt")
                process_video(video_path, output_path)

if __name__ == "__main__":
    directory = "./data"
    process_directory(directory)