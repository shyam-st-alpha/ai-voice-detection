import os
import numpy as np
import librosa
import tensorflow as tf
from tensorflow.keras import layers, models

MODEL_PATH = "cnn_model.h5"

# 🎧 Convert to spectrogram
def extract_spectrogram(file_path):
    audio, sr = librosa.load(file_path, sr=22050)

    spec = librosa.feature.melspectrogram(y=audio, sr=sr)
    spec_db = librosa.power_to_db(spec, ref=np.max)

    # Fix size
    spec_db = spec_db[:128, :128]

    return spec_db.reshape(128, 128, 1)

# 🧠 Build CNN
def build_model():
    model = models.Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=(128,128,1)),
        layers.MaxPooling2D(2,2),

        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),

        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(2, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

# 🏋️ Train
def train():
    X, y = [], []

    folders = {
        "dataset/real": 0,
        "dataset/ai": 1
    }

    print("🔥 Training CNN...")

    for folder, label in folders.items():
        for file in os.listdir(folder):
            path = os.path.join(folder, file)

            try:
                spec = extract_spectrogram(path)
                X.append(spec)
                y.append(label)
            except:
                print("Skipped:", file)

    X = np.array(X)
    y = np.array(y)

    model = build_model()
    model.fit(X, y, epochs=10)

    model.save(MODEL_PATH)
    print("✅ CNN Model Saved!")

# 🔍 Predict
def predict(file_path):
    model = tf.keras.models.load_model(MODEL_PATH)

    spec = extract_spectrogram(file_path)
    spec = np.expand_dims(spec, axis=0)

    pred = model.predict(spec)[0]

    label = np.argmax(pred)
    confidence = float(np.max(pred) * 100)

    return {
        "label": "Real Voice" if label == 0 else "AI Voice",
        "confidence": round(confidence, 2)
    }

if __name__ == "__main__":
    train()