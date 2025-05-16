import cv2
import os
import time

# Standard dimensions for face images
TARGET_WIDTH = 100
TARGET_HEIGHT = 100

def capture_samples(user_id, user_name, sample_count=30):
    """Capture face samples using external camera"""
    # Create directories if they don't exist
    if not os.path.exists('face_recognition/dataset'):
        os.makedirs('face_recognition/dataset')
    
    # Initialize external camera (index 1)
    cam = cv2.VideoCapture(1)
    if not cam.isOpened():
        print("[ERROR] Could not open external camera")
        return False
    
    # Set camera resolution
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Load Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    print(f"\n[INFO] Using EXTERNAL camera to capture {sample_count} faces for {user_name}")
    print("[INFO] Please look directly at the camera and move slightly")
    print("[INFO] Press ESC to cancel registration")
    
    count = 0
    last_capture_time = time.time()
    
    while count < sample_count:
        ret, frame = cam.read()
        if not ret:
            print("[WARNING] Could not read frame from camera")
            continue
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with enhanced parameters
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=6,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        for (x, y, w, h) in faces:
            # Only capture once per second
            if time.time() - last_capture_time < 0.5:
                continue
                
            # Add 25% padding around the face
            padding = int(0.25 * min(w, h))
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(frame.shape[1], x + w + padding)
            y2 = min(frame.shape[0], y + h + padding)
            
            # Extract face region
            face_roi = gray[y1:y2, x1:x2]
            
            # Skip if face is too small
            if face_roi.shape[0] < 50 or face_roi.shape[1] < 50:
                continue
                
            # Resize to standard dimensions
            face_resized = cv2.resize(face_roi, (TARGET_WIDTH, TARGET_HEIGHT))
            
            # Save the image
            count += 1
            img_path = f"face_recognition/dataset/User.{user_id}.{count}.jpg"
            cv2.imwrite(img_path, face_resized)
            last_capture_time = time.time()
            
            # Display status
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Captured: {count}/{sample_count}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Show the frame with detection
            cv2.imshow('Face Registration - Press ESC to quit', frame)
        
        # Exit if ESC pressed
        if cv2.waitKey(30) & 0xFF == 27:
            break
    
    # Release resources
    cam.release()
    cv2.destroyAllWindows()
    
    # Verify we captured enough samples
    if count < sample_count:
        print(f"[WARNING] Only captured {count} of {sample_count} samples")
        return False
    
    print("[INFO] Face samples captured successfully")
    return True