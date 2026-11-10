from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
from kivymd.uix.card import MDCard

try:
    from kivymd.uix.button import MDButton, MDButtonText
    def make_action_button(text, on_release):
        btn = MDButton(MDButtonText(text=text))
        btn.bind(on_release=on_release)
        return btn
except ImportError:
    from kivymd.uix.button import MDRaisedButton
    def make_action_button(text, on_release):
        return MDRaisedButton(text=text, on_release=on_release)

from storage.image_manager import StorageManager

class GalleryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_dialog = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        top_bar = MDBoxLayout(size_hint_y=None, height="48dp", padding="8dp")
        btn_back = MDIconButton(icon="arrow-left", on_release=lambda x: self.switch_screen("home"))
        title = MDLabel(text="Local Vintage Photos")

        top_bar.add_widget(btn_back)
        top_bar.add_widget(title)
        root.add_widget(top_bar)

        self.scroll = MDScrollView()
        self.grid = MDGridLayout(cols=2, spacing="12dp", padding="12dp", size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        root.add_widget(self.scroll)

        self.add_widget(root)

    def on_enter(self, *args):
        self.load_gallery()

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

    def load_gallery(self):
        self.grid.clear_widgets()
        images = StorageManager.list_saved_images()

        if not images:
            self.grid.add_widget(MDLabel(text="No saved vintage photos found.", halign="center", size_hint_y=None, height="64dp"))
            return

        for img_path in images:
            card = MDCard(size_hint=(1, None), height="180dp", radius=[12, 12, 12, 12])
            box = MDBoxLayout(orientation="vertical")
            thumb = AsyncImage(source=img_path, allow_stretch=True, keep_ratio=False)
            
            footer = MDBoxLayout(size_hint_y=None, height="36dp", padding="4dp")
            btn_del = MDIconButton(icon="delete-outline", on_release=lambda btn, p=img_path: self.confirm_delete(p))
            btn_view = MDIconButton(icon="eye-outline", on_release=lambda btn, p=img_path: self.open_image_viewer(p))
            footer.add_widget(btn_view)
            footer.add_widget(btn_del)

            box.add_widget(thumb)
            box.add_widget(footer)
            card.add_widget(box)
            self.grid.add_widget(card)

    def confirm_delete(self, path):
        btns = [
            make_action_button("CANCEL", lambda x: self.active_dialog.dismiss()),
            make_action_button("DELETE", lambda x: self._perform_delete(path))
        ]
        self.active_dialog = MDDialog(
            title="Delete Image?",
            text="Remove this image from your local device permanent storage?",
            buttons=btns
        )
        self.active_dialog.open()

    def _perform_delete(self, path):
        StorageManager.delete_image(path)
        if self.active_dialog:
            self.active_dialog.dismiss()
        self.load_gallery()

    def open_image_viewer(self, path):
        viewer = MDDialog(
            title="Vintage Image Viewer",
            type="custom",
            content_cls=AsyncImage(source=path, size_hint_y=None, height="320dp"),
            buttons=[make_action_button("CLOSE", lambda x: viewer.dismiss())]
        )
        viewer.open()
