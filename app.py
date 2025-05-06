from flask import Flask, render_template, request, redirect, url_for, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from app import app
import os
import subprocess

app = Flask(__name__, instance_relative_config=True) # initiates a flask app

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, default="Unknown")


def cleanup_missing_files():
    """Remove database entries for files that no longer exist"""
    images = Image.query.all()
    removed_count = 0

    for image in images:
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)
        if not os.path.exists(file_path):
            db.session.delete(image)
            removed_count += 1

    if removed_count > 0:
        db.session.commit()
        print(f"Removed {removed_count} entries for missing files")

@app.route("/")
def home():
    cleanup_missing_files()
    images = Image.query.all()
    return render_template("index.html", images=images)  # Load the webpage

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/guidelines")
def guidelines():
    return render_template("guidelines.html")

@app.route("/profile")
def profile() :
    return render_template("profile.html")

@app.route("/update_name", methods=["POST"])
def update_name():
    data = request.get_json()
    image_id = int(data["id"])
    new_name = data["name"]

    # Find image in database & update name
    image = Image.query.get(image_id)
    if image:

        # Get the current folder and filename
        current_relative_path = image.filename  # example: "OldName/oldname.jpg"
        current_folder = os.path.dirname(current_relative_path)  # "OldName"
        filename = os.path.basename(current_relative_path)  # "oldname.jpg"

        # Create the new folder path
        new_folder_path = os.path.join(UPLOAD_FOLDER, new_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Move the file
        old_file_path = os.path.join(UPLOAD_FOLDER, current_relative_path)
        new_file_path = os.path.join(new_folder_path, filename)

        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)

        # Remove the old (empty) folder
        old_folder_path = os.path.join(UPLOAD_FOLDER, current_folder)
        if os.path.exists(old_folder_path) and not os.listdir(old_folder_path):
            os.rmdir(old_folder_path)

        new_relative_path = os.path.join(new_name, filename)
        image.filename = new_relative_path
        image.name = new_name
        db.session.commit()

        return jsonify({"message": "Name updated successfully!"})

    return jsonify({"message": "Image not found"}), 404

@app.route('/delete_image', methods=['POST'])
def delete_image():
    data = request.get_json()
    image_id = data.get("id")

    image = db.session.get(Image, image_id)
    if image:

        image_path = os.path.join(current_app.root_path, 'static', 'uploads', image.filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        db.session.delete(image)
        db.session.commit()
        return jsonify({"message": "Image deleted successfully!"})
    else:
        return jsonify({"message": "Image not found."}), 404

@app.route("/upload", methods=["POST"])
def upload():
    """Handles file uploads"""
    if "file" not in request.files:
        return redirect(request.url)

    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)

    if file:
        filename = file.filename

        person_folder = os.path.join(UPLOAD_FOLDER, os.path.splitext(filename)[0])
        os.makedirs(person_folder, exist_ok=True)

        file_path = os.path.join(person_folder, filename)
        file.save(file_path)

        new_image = Image(filename=os.path.join(os.path.basename(person_folder), filename))
        db.session.add(new_image)
        db.session.commit()

        return redirect(url_for("home"))

@app.route("/start_camera")
def start_camera():
    subprocess.Popen(["python", "camera.py"]) # launches the camera function
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
