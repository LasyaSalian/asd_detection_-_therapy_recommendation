import tensorflow as tf

# Define the path to the trained model
MODEL_PATH = "model/inception_100.h5"

# Load the trained model
model = tf.keras.models.load_model(MODEL_PATH)

print(f"✅ Trained model loaded successfully from {MODEL_PATH}")
