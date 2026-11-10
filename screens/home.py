from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from plyer import filechooser

# Support both KivyMD 1.x and 2.0+
try:
    from kivymd.uix.button import MDRaisedButton, MDFlatButton
    from kivymd.uix.label import MDLabel
    LEGACY_KIVYMD = True
except ImportError:
    from kivymd.uix.button import MDButton, MDButtonText
    from kivymd.uix.label import MDLabel
    LEGACY_KIVYMD = False

class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.privacy_dialog = None
        self._build_ui()

    def _build_ui(self):
        layout = MDBoxLayout(
            orientation="vertical",
            padding="24dp",
            spacing="16dp",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        if LEGACY_KIVYMD:
            title = MDLabel(text="RetroLens CNN", halign="center", font_style="H4", size_hint_y=None, height="48dp")
            subtitle = MDLabel(text="100% Offline On-Device Neural Style Transfer", halign="center", font_style="Caption", theme_text_color="Secondary", size_hint_y=None, height="32dp")
            
            btn_select = MDRaisedButton(text="SELECT PHOTO", pos_hint={"center_x": 0.5}, size_hint=(0.8, None), height="48dp", on_release=self.open_file_selector)
            btn_gallery = MDRaisedButton(text="VIEW SAVED ALBUM", pos_hint={"center_x": 0.5}, size_hint=(0.8, None), height="48dp", on_release=lambda x: self.switch_screen("gallery"))
            btn_privacy = MDFlatButton(text="Privacy Guarantee", pos_hint={"center_x": 0.5}, on_release=self.show_privacy_dialog)
        else:
            title = MDLabel(text="RetroLens CNN", halign="center", role="large", size_hint_y=None, height="48dp")
            subtitle = MDLabel(text="100% Offline On-Device Neural Style Transfer", halign="center", role="small", theme_text_color="Secondary", size_hint_y=None, height="32dp")
            
            btn_select = MDButton(MDButtonText(text="SELECT PHOTO"), pos_hint={"center_x": 0.5}, size_hint=(0.8, None), height="48dp", on_release=self.open_file_selector)
            btn_gallery = MDButton(MDButtonText(text="VIEW SAVED ALBUM"), pos_hint={"center_x": 0.5}, size_hint=(0.8, None), height="48dp", on_release=lambda x: self.switch_screen("gallery"))
            btn_privacy = MDButton(MDButtonText(text="Privacy Guarantee"), style="text", pos_hint={"center_x": 0.5}, on_release=self.show_privacy_dialog)

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(btn_select)
        layout.add_widget(btn_gallery)
        layout.add_widget(btn_privacy)
        self.add_widget(layout)

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

    def open_file_selector(self, *args):
        filters = [("Images (*.jpg, *.jpeg, *.png, *.webp)", "*.jpg", "*.jpeg", "*.png", "*.webp")]
        filechooser.open_file(title="Pick an image for vintage stylization", filters=filters, on_selection=self._handle_selection)

    def _handle_selection(self, selection):
        if selection and len(selection) > 0:
            editor = self.manager.get_screen("editor")
            editor.set_image(selection[0])
            self.manager.current = "editor"

    def show_privacy_dialog(self, *args):
        privacy_text = (
            "All images are processed and stored locally on your device. "
            "No image is uploaded, transmitted, or stored on any cloud server.\n\n"
            "- Zero Network Access\n"
            "- Zero Telemetry/Analytics\n"
            "- On-Device Neural Processing"
        )
        if not self.privacy_dialog:
            if LEGACY_KIVYMD:
                dismiss_btn = MDFlatButton(text="UNDERSTOOD", on_release=lambda x: self.privacy_dialog.dismiss())
            else:
                dismiss_btn = MDButton(MDButtonText(text="UNDERSTOOD"), style="text", on_release=lambda x: self.privacy_dialog.dismiss())
            
            self.privacy_dialog = MDDialog(
                title="Strict Privacy Notice",
                text=privacy_text,
                buttons=[dismiss_btn],
            )
        self.privacy_dialog.open()
