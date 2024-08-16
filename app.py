import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask, jsonify, Response, request
from model import download_data, format_data, train_model
from config import model_file_path

app = Flask(__name__)

def update_data():
    """Download price data, format data, and train the model."""
    try:
        download_data()
        format_data()
        train_model()
        print("Data updated and model trained successfully.")
    except Exception as e:
        print(f"Error updating data: {e}")
        raise

def get_inference(token):
    """Load model and predict the price based on token."""
    try:
        with open(model_file_path, "rb") as f:
            model = pickle.load(f)
        
        now_timestamp = pd.Timestamp(datetime.now()).timestamp()
        X_new = np.array([now_timestamp]).reshape(-1, 1)
        prediction = model.predict(X_new)
        
        return prediction[0][0]
    except Exception as e:
        print(f"Error getting inference: {e}")
        raise

@app.route("/inference", methods=["GET"])
def generate_inference():
    """Generate inference for given token."""
    token = request.args.get("token")
    if not token or token != "ETH":
        error_msg = "Token is required" if not token else "Token not supported"
        return jsonify({"error": error_msg}), 400

    try:
        inference = get_inference(token)
        return jsonify({"prediction": inference}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/update", methods=["POST"])
def update():
    """Update data and return status."""
    try:
        update_data()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)}), 500

if __name__ == "__main__":
    update_data()
    app.run(host="0.0.0.0", port=8000, debug=True)
