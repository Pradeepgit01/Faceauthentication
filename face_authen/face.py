


import cv2
import face_recognition
import mysql.connector
import numpy as np

# MySQL connection
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="face_authentication"
    )

# Encode a face from an image
def encode_face(image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_image)
    if len(face_encodings) > 0:
        return face_encodings[0]
    return None

# Add user to the database
def add_user(name, encoding):
    db = connect_to_db()
    cursor = db.cursor()
    encoding_bytes = encoding.tobytes()
    query = "INSERT INTO users (name, face_encoding) VALUES (%s, %s)"
    cursor.execute(query, (name, encoding_bytes))
    db.commit()
    db.close()

# Fetch all users from the database
def fetch_users():
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, face_encoding FROM users")
    users = cursor.fetchall()
    db.close()

    user_data = []
    for user in users:
        user_id, name, encoding = user
        encoding_np = np.frombuffer(encoding, dtype=np.float64)
        user_data.append((user_id, name, encoding_np))
    
    return user_data


# Authenticate user based on face
def authenticate_user(frame, known_users):
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if len(face_encodings) > 0:
        for i, face_encoding in enumerate(face_encodings):
            for user_id, name, stored_encoding in known_users:
                match = face_recognition.compare_faces([stored_encoding], face_encoding)
                if match[0]:
                    return name, face_locations[i]  # Return the name and corresponding face location
    return None, None

# Main function with updated name display
def main():
    video_capture = cv2.VideoCapture(0)
    known_users = fetch_users()

    while True:
        ret, frame = video_capture.read()
        
        if not ret:
            print("Error accessing camera. Exiting...")
            break

        # Authenticate face
        user, face_location = authenticate_user(frame, known_users)

        if user:
            message = f"Authenticated: {user}"
        else:
            message = "Unknown User - Press 'a' to add"

        # Display message on the frame
        cv2.putText(frame, message, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (51, 247, 1), 2, cv2.LINE_AA)

        if face_location:
            top, right, bottom, left = face_location
            # Draw rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Display user's name below the rectangle
            cv2.rectangle(frame, (left, bottom + 20), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, user, (left + 6, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Show the resulting frame
        cv2.imshow('Face Authentication', frame)

        # Handle keypress events
        key = cv2.waitKey(1) & 0xFF

        # Quit on pressing 'q'
        if key == ord('q'):
            break

        # Add new user on pressing 'a'
        if not user and key == ord('a'):
            # Ask for the user's name
            name = input("Enter the name of the new user: ")

            # Encode the current frame as the face for the new user
            face_encoding = encode_face(frame)

            if face_encoding is not None:
                add_user(name, face_encoding)
                known_users = fetch_users()  # Refresh known users
                print(f"New user '{name}' added successfully!")
            else:
                print("Failed to capture a valid face for encoding.")

    # Release the video capture
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
