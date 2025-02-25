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
    """Render the dashboard."""
    return render_template("dashboard.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handles file upload and loads the dataset into memory."""
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


@app.route("/prepare_dataset", methods=["POST"])
def prepare_dataset():
    """Converts dataset into LLM-friendly structured text format."""
    global dataset
    if dataset is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        # Convert each row into a structured text format
        dataset["LLM_Input"] = dataset.apply(lambda row: " | ".join([f"{col}: {str(row[col])}" for col in dataset.columns]), axis=1)
        return jsonify({"message": "Dataset converted for LLM processing successfully!"})
    except Exception as e:
        return jsonify({"error": f"Error processing dataset: {str(e)}"}), 500


@app.route("/ask", methods=["POST"])
def ask_ai():
    """Handles user queries about the dataset using LLM logic."""
    global dataset
    if dataset is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    data = request.get_json()
    question = data.get("question", "").lower()

    # LLM-style response logic
    if "top phishing indicators" in question:
        indicators = dataset.columns[:5].tolist()
        response = f"The top phishing indicators are: {', '.join(indicators)}."
    elif "rows" in question:
        response = f"The dataset contains {dataset.shape[0]} rows."
    elif "columns" in question:
        response = f"The dataset has the following columns: {', '.join(dataset.columns)}."
    else:
        response = "I am unable to understand the question. Please ask about phishing indicators, rows, or columns."

    return jsonify({"answer": response})


@app.route("/predict", methods=["POST"])
def predict():
    """Handles phishing attack detection using LLM-based structured text input."""
    global dataset
    if dataset is None:
        return jsonify({"error": "No dataset uploaded"}), 400

    try:
        data = request.get_json()
        # Generate LLM-compatible text input
        llm_input = f"URL: {data.get('URL')} | URL Length: {data.get('URLLength')} | Domain: {data.get('Domain')} | Domain Length: {data.get('DomainLength')}"

        # LLM-based reasoning (Mock Example)
        if "login" in data.get("URL", "").lower() or int(data.get("URLLength", 0)) > 75:
            prediction = "Highly Suspicious - Potential Phishing"
        else:
            prediction = "Likely Safe - No Immediate Threat"

        return jsonify({"prediction": prediction})

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
