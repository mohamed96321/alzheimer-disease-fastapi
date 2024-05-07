import tensorflow as tf
import numpy as np
from PIL import Image as PILImage

# Define image predictor class
class ImagePredictor:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        try:
            model = tf.saved_model.load(model_path)
            print("Loaded model successfully")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError("Failed to load model")
        
    def preprocess_image(self, image_path):
        # Load image using PIL
        img = PILImage.open(image_path)

        # Convert image to RGB if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize image to (150, 150)
        img = img.resize((150, 150))

        # Convert image to numpy array
        img_array = np.array(img)

        # Normalize pixel values to range [0, 1]
        img_array = img_array.astype(np.float32) / 255.0

        # Ensure image has 3 channels (RGB)
        if img_array.shape[-1] != 3:
            raise ValueError("Image must have 3 channels (RGB)")

        # Expand dimensions to create batch dimension (None, 150, 150, 3)
        img_array = tf.expand_dims(img_array, axis=0)

        return img_array

    def predict_image(self, image_path):
        if self.model is None:
            raise ValueError("Model is not loaded or is invalid.")

        # Preprocess the image
        img_array = self.preprocess_image(image_path)

        try:
            # Perform inference
            predictions = self.model(img_array)
            predicted_class_index = np.argmax(predictions)
            return float(predicted_class_index)  # Convert prediction to float
        except Exception as e:
            print(f"Error predicting image: {e}")
            raise RuntimeError("Failed to predict image")
