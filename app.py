from flask_cors import CORS
from flask import Flask, request, jsonify
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from werkzeug.utils import secure_filename
import mysql.connector
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Upload folder config
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load pre-trained model
MODEL_PATH = "model/inception_100.h5"
model = load_model(MODEL_PATH)

# Allowed file types
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "asd_detection_db"
}

# Therapy Recommendations
THERAPY_RECOMMENDATIONS = {
    "Autistic": [
        "Applied Behavior Analysis (ABA)",
        "Cognitive Behavioral Therapy (CBT)",
        "Speech Therapy",
        "Occupational Therapy (OT)",
        "Sensory Integration Therapy",
        "Music Therapy"
    ],
    "Non-Autistic": ["No therapy recommendations needed."]
}

# Check allowed file
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Image preprocessing
def preprocess_image(image_path):
    img = load_img(image_path, target_size=(150, 150))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

# Home Route
@app.route("/")
def home():
    return "ASD Detection API is running!"

# Predict Route
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Predict
        img = preprocess_image(file_path)
        raw_prediction = model.predict(img)
        confidence_score = float(raw_prediction[0][0])
        label = "Non-Autistic" if confidence_score > 0.5 else "Autistic"
        confidence_percent = confidence_score * 100 if label == "Non-Autistic" else (1 - confidence_score) * 100

        # Save to DB
        save_result(filename, label, confidence_percent)

        return jsonify({
            "filename": filename,
            "prediction": label,
            "confidence": f"{confidence_percent:.2f}%",
            "therapy_recommendations": THERAPY_RECOMMENDATIONS[label]
        })

    return jsonify({"error": "Invalid file format"}), 400

# Save to DB
def save_result(filename, prediction, confidence):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (filename, prediction, confidence) VALUES (%s, %s, %s)",
            (filename, prediction, confidence)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database Error:", e)

# Get all results
@app.route("/results", methods=["GET"])
def get_results():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT filename, prediction, confidence, timestamp FROM predictions ORDER BY timestamp DESC")
        data = cursor.fetchall()
        conn.close()

        results = [
            {
                "filename": row[0],
                "prediction": row[1],
                "confidence": f"{row[2]:.2f}%",
                "timestamp": row[3].strftime('%d/%m/%Y, %I:%M:%S %p')
            }
            for row in data
        ]

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Analysis route
@app.route("/analysis", methods=["GET"])
def get_analysis():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT prediction, COUNT(*) FROM predictions GROUP BY prediction")
        data = cursor.fetchall()
        conn.close()

        analysis_data = {row[0]: row[1] for row in data}
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Therapy route
@app.route("/therapy", methods=["GET"])
def get_therapy_recommendations():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT prediction FROM predictions ORDER BY timestamp DESC LIMIT 1")
        latest = cursor.fetchone()
        conn.close()

        if latest:
            diagnosis = latest[0]
            therapies = THERAPY_RECOMMENDATIONS.get(diagnosis, [])
        else:
            diagnosis = "Unknown"
            therapies = ["No previous prediction found."]

        return jsonify({"diagnosis": diagnosis, "therapy_recommendations": therapies})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
