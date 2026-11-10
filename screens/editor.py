import os
import threading
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton

# Robust button import for KivyMD 2.0
try:
    from kivymd.uix.button import MDButton, MDButtonText
    def create_button(text, on_release=None, disabled=False):
        btn = MDButton(
            MDButtonText(text=text),
            size_hint_x=0.5,
            disabled=disabled
        )
        if on_release:
            btn.bind(on_release=on_release)
        return btn
except (ImportError, AttributeError):
    from kivymd.uix.button import MDRaisedButton
    def create_button(text, on_release=None, disabled=False):
        return MDRaisedButton(
            text=text,
            size_hint_x=0.5,
            disabled=disabled,
            on_release=on_release
        )

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
        btn_back = MDIconButton(icon="arrow-left", on_release=lambda x: self.navigate_back())
        top_bar.add_widget(btn_back)
        root.add_widget(top_bar)

        # Image Previews
        self.preview_container = MDBoxLayout(orientation="horizontal", spacing="8dp")
        self.original_view = Image(allow_stretch=True, keep_ratio=True)
        self.processed_view = Image(allow_stretch=True, keep_ratio=True)
        self.preview_container.add_widget(self.original_view)
        self.preview_container.add_widget(self.processed_view)
        root.add_widget(self.preview_container)

        # Universal ProgressBar (no dependency on fluctuating KivyMD spinner modules)
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height="8dp", value=0)
        root.add_widget(self.progress_bar)

        # Bottom Actions
        actions = MDBoxLayout(size_hint_y=None, height="56dp", spacing="12dp")
        self.btn_apply = create_button("APPLY CNN VINTAGE", on_release=self.run_conversion_threaded)
        self.btn_save = create_button("SAVE TO ALBUM", on_release=self.save_final_image, disabled=True)

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
        self.progress_bar.value = 0

    def run_conversion_threaded(self, *args):
        if not self.current_source:
            return
        self.btn_apply.disabled = True
        self.progress_bar.value = 40
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
        self.progress_bar.value = 100
        self.btn_apply.disabled = False
        self.btn_save.disabled = False

    def save_final_image(self, *args):
        if self.temp_processed and os.path.exists(self.temp_processed):
            saved_dest = StorageManager.save_processed_image(self.temp_processed)
            self.btn_save.disabled = True
            self.progress_bar.value = 0

    def navigate_back(self):
        self.manager.current = "home"
