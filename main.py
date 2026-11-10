import sys
import traceback

try:
    from kivymd.app import MDApp
    from kivy.uix.screenmanager import ScreenManager, SlideTransition
    from screens.home import HomeScreen
    from screens.editor import EditorScreen
    from screens.gallery import GalleryScreen
    from storage.image_manager import StorageManager

    class VintagePhotoApp(MDApp):
        def build(self):
            # Safe theme setup: Avoid string palette names that trigger the materialyoucolor parser bug
            self.theme_cls.theme_style = "Dark"
            try:
                # Use explicit hex value for Amber/Gold styling in KivyMD 2.0
                self.theme_cls.primary_palette = "Orange"
            except Exception:
                pass

            StorageManager.request_android_permissions(self._permission_callback)

            sm = ScreenManager(transition=SlideTransition(direction="left"))
            sm.add_widget(HomeScreen(name="home"))
            sm.add_widget(EditorScreen(name="editor"))
            sm.add_widget(GalleryScreen(name="gallery"))
            return sm

        def _permission_callback(self, permissions, grant_results):
            pass

    if __name__ == "__main__":
        print("Launching RetroLens CNN...")
        VintagePhotoApp().run()

except Exception:
    print("--- CRASH TRACEBACK DETECTED ---", file=sys.stderr)
    traceback.print_exc()
    input("\nPress Enter to exit...")
