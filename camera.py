import cv2
from deepface import DeepFace
import os
import glob


def recognize_faces():
    # debugging
    print("Checking database directory...")
    uploads_dir = "static/uploads"

    # Find all image files in all subdirectories
    image_paths = []
    for root, dirs, files in os.walk(uploads_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_paths.append(os.path.join(root, file))

    if not image_paths:
        print("No images found in database directory or subdirectories")
        return
    else:
        print(f"Found {len(image_paths)} images in database")
        for path in image_paths:
            print(f"  - {path}")

    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
    cap = cv2.VideoCapture(0)  # Open webcam

    # debugging
    if not cap.isOpened():
        print("Failed to open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        temp_frame_path = "static/temp_frame.jpg"
        cv2.imwrite(temp_frame_path, frame)  # Save the frame temporarily

        try:
            for ref_img_path in image_paths:
                try:
                    result = DeepFace.verify(
                        img1_path=temp_frame_path,
                        img2_path=ref_img_path,
                        model_name="VGG-Face",
                        enforce_detection=False
                    )

                    if result["verified"]:
                        # Extract person name from directory name
                        person_dir = os.path.basename(os.path.dirname(ref_img_path))
                        cv2.putText(frame, person_dir, (50, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        print(f"Match found: {person_dir}")
                        break  # Stop after first match

                except Exception as e:
                    continue

        except Exception as e:
            print(f"Recognition error: {e}")

        cv2.imshow("Face Recognition", frame)

        if os.path.exists(temp_frame_path):
            os.remove(temp_frame_path)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    recognize_faces()