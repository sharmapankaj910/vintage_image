import os
import threading
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import Snackbar
from kivy.uix.image import Image

from models.vintage_converter import VintageCNNConverter
from storage.image_manager import StorageManager

class EditorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.converter = VintageCNNConverter()
        self.current_source = None
        self.temp_processed = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical", spacing="8dp", padding="12dp")

        # Top Bar
        top_bar = MDBoxLayout(size_hint_y=None, height="48dp")
        btn_back = MDIconButton(
            icon="arrow-left",
            on_release=lambda x: self.navigate_back()
        )
        top_bar.add_widget(btn_back)
        root.add_widget(top_bar)

        # Previews layout
        self.preview_container = MDBoxLayout(orientation="horizontal", spacing="8dp")
        self.original_view = Image(allow_stretch=True, keep_ratio=True)
        self.processed_view = Image(allow_stretch=True, keep_ratio=True)
        self.preview_container.add_widget(self.original_view)
        self.preview_container.add_widget(self.processed_view)
        root.add_widget(self.preview_container)

        # Progress spinner
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=("40dp", "40dp"),
            pos_hint={"center_x": 0.5},
            active=False
        )
        root.add_widget(self.spinner)

        # Bottom Actions
        actions = MDBoxLayout(size_hint_y=None, height="56dp", spacing="12dp")
        self.btn_apply = MDRaisedButton(
            text="APPLY CNN VINTAGE",
            size_hint_x=0.5,
            on_release=self.run_conversion_threaded
        )
        self.btn_save = MDRaisedButton(
            text="SAVE TO ALBUM",
            size_hint_x=0.5,
            disabled=True,
            on_release=self.save_final_image
        )
        actions.add_widget(self.btn_apply)
        actions.add_widget(self.btn_save)
        root.add_widget(actions)

        self.add_widget(root)

    def set_image(self, file_path: str):
        self.current_source = file_path
        self.temp_processed = None
        self.original_view.source = file_path
        self.original_view.reload()
        self.processed_view.source = ""
        self.btn_save.disabled = True

    def run_conversion_threaded(self, *args):
        if not self.current_source:
            return
        self.btn_apply.disabled = True
        self.spinner.active = True
        # Execute model inference on background worker to prevent UI freezing
        threading.Thread(target=self._worker_infer, daemon=True).start()

    def _worker_infer(self):
        cache_dir = os.path.join(StorageManager.get_save_directory(), ".cache")
        os.makedirs(cache_dir, exist_ok=True)
        out_path = os.path.join(cache_dir, "temp_render.jpg")

        self.converter.process(self.current_source, out_path)
        Clock.schedule_once(lambda dt: self._on_processing_complete(out_path), 0)

    def _on_processing_complete(self, out_path):
        self.temp_processed = out_path
        self.processed_view.source = out_path
        self.processed_view.reload()
        self.spinner.active = False
        self.btn_apply.disabled = False
        self.btn_save.disabled = False
        Snackbar(text="Vintage filter successfully applied!").open()

    def save_final_image(self, *args):
        if self.temp_processed and os.path.exists(self.temp_processed):
            saved_dest = StorageManager.save_processed_image(self.temp_processed)
            Snackbar(text=f"Saved locally: {os.path.basename(saved_dest)}").open()
            self.btn_save.disabled = True

    def navigate_back(self):
        self.manager.current = "home"