import os
import cv2
import numpy as np
from PIL import Image

# Suppress TF C++ and Python debug registration messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    try:
        import tensorflow.lite as tflite
    except ImportError:
        tflite = None

class VintageCNNConverter:
    def __init__(self, model_path: str = "cnn_model/vintage_model.tflite"):
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self._load_model()

    def _load_model(self):
        if tflite is not None and os.path.exists(self.model_path):
            try:
                self.interpreter = tflite.Interpreter(model_path=self.model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
            except Exception:
                self.interpreter = None

    def _apply_vignette(self, image: np.ndarray, strength: float = 0.4) -> np.ndarray:
        rows, cols = image.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        
        vignette = np.copy(image).astype(np.float32)
        for i in range(3):
            vignette[:, :, i] = vignette[:, :, i] * ((1 - strength) + strength * mask)
        return np.clip(vignette, 0, 255).astype(np.uint8)

    def _apply_film_grain(self, image: np.ndarray, intensity: float = 12.0) -> np.ndarray:
        h, w, c = image.shape
        noise = np.random.normal(0, intensity, (h, w, c))
        noisy_image = image.astype(np.float32) + noise
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def _apply_sepia(self, image: np.ndarray) -> np.ndarray:
        sepia_matrix = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        sepia_img = cv2.transform(image, sepia_matrix)
        return np.clip(sepia_img, 0, 255).astype(np.uint8)

    def process(self, source_image_path: str, output_path: str) -> str:
        with Image.open(source_image_path) as pil_img:
            pil_img = pil_img.convert("RGB")
            orig_w, orig_h = pil_img.size

            max_dim = 1920
            if max(orig_w, orig_h) > max_dim:
                pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            
            img_np = np.array(pil_img)

        if self.interpreter is not None:
            in_shape = self.input_details[0]["shape"]
            req_h, req_w = in_shape[1], in_shape[2]
            
            resized = cv2.resize(img_np, (req_w, req_h), interpolation=cv2.INTER_AREA)
            input_tensor = np.expand_dims(resized.astype(np.float32) / 255.0, axis=0)
            
            self.interpreter.set_tensor(self.input_details[0]["index"], input_tensor)
            self.interpreter.invoke()
            
            output_tensor = self.interpreter.get_tensor(self.output_details[0]["index"])
            cnn_out = (np.squeeze(output_tensor) * 255.0).astype(np.uint8)
            styled = cv2.resize(cnn_out, (img_np.shape[1], img_np.shape[0]), interpolation=cv2.INTER_LINEAR)
        else:
            styled = self._apply_sepia(img_np)

        styled = self._apply_vignette(styled, strength=0.35)
        styled = self._apply_film_grain(styled, intensity=10.0)
        styled = cv2.convertScaleAbs(styled, alpha=0.92, beta=8)

        out_pil = Image.fromarray(styled)
        out_pil.save(output_path, "JPEG", quality=92)
        return output_path
