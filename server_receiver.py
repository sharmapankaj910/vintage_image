import os
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Local folder on your PC where all remote uploads will be saved
SAVE_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "VintagePhotos", "RemoteUploads")
os.makedirs(SAVE_DIR, exist_ok=True)

@app.route("/api/upload", methods=["POST"])
def receive_image():
    if "image" not in request.files:
        return jsonify({"error": "No image payload"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"remote_{timestamp}_{file.filename}"
    target_path = os.path.join(SAVE_DIR, safe_filename)

    file.save(target_path)
    print(f"[+] Successfully saved remote user photo: {safe_filename}")

    return jsonify({"status": "success", "saved_as": safe_filename}), 200

if __name__ == "__main__":
    print(f"Server active! Listening for uploads into: {SAVE_DIR}")
    app.run(host="0.0.0.0", port=5000)
