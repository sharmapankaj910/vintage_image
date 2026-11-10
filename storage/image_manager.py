import os
import shutil
from datetime import datetime
from kivy.utils import platform

class StorageManager:
    @staticmethod
    def get_save_directory() -> str:
        if platform == "android":
            from android.storage import primary_external_storage_path
            primary_ext = primary_external_storage_path()
            save_dir = os.path.join(primary_ext, "Pictures", "VintagePhotos")
        else:
            save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "VintagePhotos")
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

    @classmethod
    def save_processed_image(cls, temp_file_path: str) -> str:
        save_dir = cls.get_save_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = os.path.join(save_dir, f"vintage_{timestamp}.jpg")
        shutil.copyfile(temp_file_path, target_path)
        return target_path

    @classmethod
    def list_saved_images(cls) -> list:
        save_dir = cls.get_save_directory()
        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        if not os.path.exists(save_dir):
            return []
        files = [
            os.path.join(save_dir, f)
            for f in os.listdir(save_dir)
            if f.lower().endswith(valid_exts)
        ]
        files.sort(key=os.path.getmtime, reverse=True)
        return files

    @classmethod
    def delete_image(cls, file_path: str) -> bool:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except OSError:
                return False
        return False

    @staticmethod
    def request_android_permissions(callback=None):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            permissions = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ]
            request_permissions(permissions, callback)
        elif callback:
            callback([], [])
