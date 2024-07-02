import os
import shutil

def organize_videos_by_folder(directory):
    # Проверяем, существует ли директория
    if not os.path.exists(directory):
        print(f"Директория {directory} не существует.")
        return

    # Проходим по всем файлам в директории
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Проверяем, является ли файл видео (можно добавить больше расширений при необходимости)
        if os.path.isfile(file_path) and filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            # Удаляем расширение файла, чтобы получить имя папки
            folder_name = os.path.splitext(filename)[0]
            folder_path = os.path.join(directory, folder_name)

            # Создаем папку, если она не существует
            os.makedirs(folder_path, exist_ok=True)

            # Перемещаем файл в соответствующую папку
            new_file_path = os.path.join(folder_path, filename)
            shutil.move(file_path, new_file_path)
            print(f'Файл {filename} перемещен в папку {folder_name}')

if __name__ == "__main__":
    # Укажите путь к директории с видеофайлами
    directory = "./data"
    organize_videos_by_folder(directory)