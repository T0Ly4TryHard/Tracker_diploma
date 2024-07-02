import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import os

# Задаем возможные трекеры и их пути
TRACKERS = {
    "VIT2": ("VIT2.tracker", "VIT2.wrapper", "Tracker", "TrackerWrapper", "./VIT2/MobileViTv2_Track_ep0300.onnx"),
    "nanotreackerv2": ("nanotreackv2.core.nano_tracker", "nanotreackv2.wrapper", "NanoTracker", "TrackerWrapper", None)
}

# Название трекера для использования
SELECTED_TRACKER_NAME = "nanotreackerv2"  # Укажите здесь трекер, который хотите использовать

class VideoTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Видео Трекинг")
        self.root.geometry("400x300")

        self.video_path = None

        self.label = tk.Label(root, text="Выберите видеофайл для трекинга")
        self.label.pack(pady=10)

        self.file_button = tk.Button(root, text="Выбрать видеофайл", command=self.select_file)
        self.file_button.pack(pady=10)

        self.track_button = tk.Button(root, text="Начать трекинг", command=self.start_tracking)
        self.track_button.pack(pady=10)

        self.roi = None

    def select_file(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Видео файлы", "*.mp4 *.avi *.mkv *.mov"), ("Все файлы", "*.*")]
        )
        if self.video_path:
            self.label.config(text=f"Выбран файл: {os.path.basename(self.video_path)}")

    def start_tracking(self):
        tracker_name = SELECTED_TRACKER_NAME
        if tracker_name not in TRACKERS:
            messagebox.showwarning("Ошибка", f"Трекер '{tracker_name}' не найден. Доступные трекеры: {list(TRACKERS.keys())}")
            return

        if not self.video_path:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите видеофайл")
            return

        self.roi = self.select_roi(self.video_path)
        if self.roi:
            self.track_video(self.video_path, self.roi, tracker_name)

    def select_roi(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", f"Не удалось открыть видеофайл {video_path}")
            return None

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Ошибка", f"Не удалось прочитать кадр из видеофайла {video_path}")
            return None

        cv2.putText(frame, 'Выберите ROI и нажмите ENTER', (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Выбор ROI", frame)
        
        x, y, w, h = cv2.selectROI("Выбор ROI", frame, fromCenter=False)
        cv2.destroyWindow("Выбор ROI")
        cap.release()

        if w == 0 or h == 0:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите корректный ROI")
            return None
        
        return [x, y, w, h]

    def track_video(self, video_path, roi, tracker_name):
        module_path, wrapper_path, tracker_class, wrapper_class, model_path = TRACKERS[tracker_name]

        Tracker = self.dynamic_import(module_path, tracker_class)
        TrackerWrapper = self.dynamic_import(wrapper_path, wrapper_class)

        tracker = Tracker(model_path=model_path) if model_path else Tracker()
        tracker_wrapper = TrackerWrapper(tracker)

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", f"Не удалось открыть видеофайл {video_path}")
            return
        
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        frame_fps = int(cap.get(5))
        output_path = f"{os.path.splitext(video_path)[0]}_{tracker_name}.avi"
        output_txt_path = f"{os.path.splitext(video_path)[0]}_{tracker_name}.txt"
        
        video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M','J','P','G'), frame_fps, (frame_width, frame_height))
        output_file = open(output_txt_path, 'w')
        
        frame_count = 0
        ret, frame = cap.read()
        frame_last = frame.copy()
        tracker_wrapper.init(frame, frame, roi)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            frame_disp = frame.copy()
            
            bbox, score, technical_rect, (x_point, y_point) = tracker_wrapper.track(frame, frame_last)
            x, y, w, h = bbox
            
            norm_x = x / frame_width
            norm_y = y / frame_height
            norm_w = w / frame_width
            norm_h = h / frame_height
            
            output_file.write(f"{frame_count} {norm_x:.6f} {norm_y:.6f} {norm_w:.6f} {norm_h:.6f}\n")
            
            x1, y1, x2, y2 = int(x), int(y), int(x + w), int(y + h)
            cv2.rectangle(frame_disp, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame_disp, (int(x_point), int(y_point)), 5, (255, 0, 255), 2)
            cv2.rectangle(frame_disp, (int(technical_rect[0]), int(technical_rect[1])), (int(technical_rect[0]+technical_rect[2]), int(technical_rect[1]+technical_rect[3])), (255, 255, 0), 2)
            cv2.putText(frame_disp, f'Tracking! {score}', (20, 130), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 1)
            cv2.putText(frame_disp, 'Press q to quit', (20, 80), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 1)
            
            frame_last = frame.copy()
            cv2.imshow('Tracking', frame_disp)
            video_writer.write(frame_disp)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        video_writer.release()
        output_file.close()
        cv2.destroyAllWindows()
        messagebox.showinfo("Информация", "Трекинг завершен успешно")

    def dynamic_import(self, module_name, class_name):
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoTrackerApp(root)
    root.mainloop()
