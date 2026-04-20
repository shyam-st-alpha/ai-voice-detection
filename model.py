import os
import numpy as np
import librosa
from sklearn.ensemble import RandomForestClassifier
import joblib
import subprocess

MODEL_PATH = "voice_model.pkl"

# 🔁 Convert any audio to WAV using FFmpeg
def convert_to_wav(input_path):
    try:
        output_path = input_path.rsplit(".", 1)[0] + ".wav"

        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return output_path

    except Exception as e:
        print(f"❌ Conversion Error: {e}")
        return None

# 🎧 Extract MFCC features
def extract_features(file_path):
    try:
        # Convert if not wav
        if not file_path.endswith(".wav"):
            file_path = convert_to_wav(file_path)

        if file_path is None or not os.path.exists(file_path):
            return None

        audio, sr = librosa.load(file_path, sr=None)
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)

        return np.mean(mfcc.T, axis=0)

    except Exception as e:
        print(f"❌ Feature Error: {e}")
        return None

# 🧠 Train model
def train_model():
    X = []
    y = []

    folders = {
        "dataset/real": 0,
        "dataset/ai": 1
    }

    print("🔥 Training Started...\n")

    for folder, label in folders.items():
        print(f"📂 Checking folder: {folder}")

        if not os.path.exists(folder):
            print(f"❌ Folder missing: {folder}")
            continue

        files = os.listdir(folder)
        print(f"➡ Found {len(files)} files")

        for file in files:
            if not file.endswith(".wav"):
                continue

            file_path = os.path.join(folder, file)
            print(f"🎧 Processing: {file}")

            features = extract_features(file_path)

            if features is not None:
                X.append(features)
                y.append(label)
            else:
                print(f"❌ Skipped: {file}")

    print(f"\nCollected samples: {len(X)}")

    if len(X) == 0:
        print("❌ No valid data found!")
        return

    print("🚀 Training model...")

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("✅ Model Trained and Saved!")

# 🔍 Predict voice
def predict(file_path):
    try:
        if not os.path.exists(MODEL_PATH):
            return {"label": "Model not trained", "confidence": 0}

        model = joblib.load(MODEL_PATH)

        features = extract_features(file_path)

        if features is None:
            return {"label": "Invalid audio", "confidence": 0}

        prediction = model.predict([features])[0]
        probabilities = model.predict_proba([features])[0]

        confidence = max(probabilities) * 100

        label = "Real Voice" if prediction == 0 else "AI Voice"

        return {
            "label": label,
            "confidence": round(confidence, 2)
        }

    except Exception as e:
        return {"label": "Error", "confidence": 0}

# ▶ Run training
if __name__ == "__main__":
    train_model()