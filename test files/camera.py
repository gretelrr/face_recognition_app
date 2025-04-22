import cv2
from deepface import DeepFace
import os

def recognize_faces():

    # claude addition v
    uploads_dir = "static/uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"Created directory: {uploads_dir}")
        print("Please add some reference images to the uploads directory")
        return

    # Check if there are any image files in the directory
    image_extensions = ['.jpg', '.jpeg', '.png']
    has_images = False
    for file in os.listdir(uploads_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            has_images = True
            break

    if not has_images:
        print("No images found in static/uploads directory. Please add some reference images.")
        return
    # claude addition

    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
    cap = cv2.VideoCapture(0)  # Open webcam

    # debugging
    if not cap.isOpened():
        print("Failed to open camera 💀")
        return

    #known_faces_dir = "static/uploads"  # Folder where uploaded images are stored

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        temp_frame_path = "static/temp_frame.jpg"
        cv2.imwrite(temp_frame_path, frame)  # Save the frame temporarily

        try:
            results = DeepFace.find(
                img_path=temp_frame_path,
                db_path="static/uploads",
                enforce_detection=False
            )

            if len(results[0]) > 0:
                best_match = results[0].iloc[0]
                identity = os.path.basename(best_match["identity"])
                name = os.path.splitext(identity)[0]

                cv2.putText(frame, name, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        except Exception as e:
            print("Recognition error:", e)

        cv2.imshow("Face Recognition", frame)

        if os.path.exists(temp_frame_path):
            os.remove(temp_frame_path)

        if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'Q' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()
