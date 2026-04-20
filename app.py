from flask import Flask, render_template, request, jsonify
import os
from model_dl import predict

print("🔥 app.py is running...")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict_voice():
    try:
        file = request.files["audio"]

        path = os.path.join("uploads", "input.webm")
        file.save(path)

        result = predict(path)

        return jsonify(result)

    except Exception as e:
        return jsonify({"label": "Server Error", "confidence": 0})
    
if __name__ == "__main__":
    print("🚀 Starting Flask Server...")
    app.run(debug=True)