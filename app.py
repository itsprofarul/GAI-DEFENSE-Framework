from flask import Flask, render_template, request, jsonify
import os
import pandas as pd

app = Flask(__name__)

# Upload Folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variable to store dataset
dataset = None

@app.route("/")
def home():
    return render_template("dashboard.html")
 
@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles file upload and loads the dataset into memory"""
    global dataset
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    
    try:
        dataset = pd.read_csv(filepath)
        return jsonify({"message": "File uploaded successfully!", "filename": file.filename})
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route("/ask", methods=["POST"])
def ask_ai():
    """Handles user queries about the dataset"""
    global dataset
    if dataset is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    data = request.get_json()
    question = data.get("question", "").lower()

    # Answer based on dataset
    if "top phishing indicators" in question:
        top_columns = dataset.columns[:5].tolist()
        response = f"Top phishing indicators: {', '.join(top_columns)}"
    elif "rows" in question:
        response = f"The dataset contains {dataset.shape[0]} rows."
    else:
        response = "I am unable to understand the question."

    return jsonify({"answer": response})

@app.route("/predict", methods=["POST"])
def predict():
    """Handles phishing attack detection based on user input"""
    global dataset
    if dataset is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        data = request.get_json()
        url_length = int(data.get("URLLength", 0))

        # Mock AI Model Prediction
        prediction = "Phishing" if url_length > 50 else "Legitimate"

        return jsonify({"prediction": prediction})

    except ValueError:
        return jsonify({"error": "Invalid input values"}), 400

if __name__ == "__main__":
    app.run(debug=True)
