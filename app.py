from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import cv2
import numpy as np
import os
import pickle
import base64
from database import Database

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/temp_faces'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize database
db = Database('voting_system.db')

# Global variables for face recognition
knn = None
h, w = None, None

def load_face_model():
    global knn, h, w
    try:
        with open('face_recognition/trainer/knn_model.pkl', 'rb') as f:
            knn = pickle.load(f)
        with open('face_recognition/trainer/model_params.pkl', 'rb') as f:
            h, w = pickle.load(f)
    except Exception as e:
        print(f"Error loading face model: {str(e)}")

load_face_model()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            aadhar = request.form['aadhar']
            
            if db.get_user_by_aadhar(aadhar):
                flash('User already registered', 'error')
                return redirect(url_for('register'))
            
            user_id = db.add_user(name, aadhar)
            
            from face_recognition.face_dataset import capture_samples
            if capture_samples(user_id, name):
                from face_recognition.face_trainer import train_model
                train_model()
                load_face_model()
                flash('Registration successful! Please sign in to vote', 'success')
                return redirect(url_for('signin'))
            else:
                flash('Face capture failed. Please try again.', 'error')
        
        except Exception as e:
            print(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/video_feed')
def video_feed():
    # Use index 1 for external camera (0 is usually built-in)
    camera = cv2.VideoCapture(1)
    
    def generate():
        while True:
            success, frame = camera.read()
            if not success:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        name = request.form['name']
        aadhar = request.form['aadhar']
        
        user = db.get_user_by_aadhar(aadhar)
        if not user or user[1] != name:
            flash('Invalid credentials', 'error')
            return redirect(url_for('signin'))
        
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        return redirect(url_for('vote'))
    
    return render_template('signin.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        try:
            if knn is None:
                flash('Face recognition system not ready', 'error')
                return redirect(url_for('vote'))
            
            # Get the base64 image data
            face_data = request.form.get('face_image')
            if not face_data or 'data:image/jpeg;base64,' not in face_data:
                flash('No face image captured', 'error')
                return redirect(url_for('vote'))
            
            # Convert base64 to image
            header, encoded = face_data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            img_array = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                flash('Could not process image', 'error')
                return redirect(url_for('vote'))
            
            # Resize to match training dimensions
            img = cv2.resize(img, (w, h))
            
            # Predict using KNN
            face_vector = img.reshape(1, -1)
            predicted_id = knn.predict(face_vector)[0]
            confidence = knn.predict_proba(face_vector)[0].max()
            
            # Verify match with signed-in user
            if confidence < 0.6 or predicted_id != session['user_id']:
                flash(f'Face verification failed (confidence: {confidence:.2f})', 'error')
                return redirect(url_for('vote'))
            
            # Process vote
            candidate_id = request.form.get('candidate')
            if not candidate_id:
                flash('Please select a candidate', 'error')
                return redirect(url_for('vote'))
            
            if db.has_voted(session['user_id']):
                flash('You have already voted', 'error')
                return redirect(url_for('vote'))
            
            db.record_vote(session['user_id'], candidate_id)
            flash('Vote recorded successfully!', 'success')
            return redirect(url_for('results'))
            
        except Exception as e:
            print(f"Voting error: {str(e)}")
            flash('Voting failed. Please try again.', 'error')
    
    candidates = db.get_candidates()
    return render_template('vote.html', 
                         candidates=candidates,
                         user_name=session.get('user_name'))

@app.route('/results')
def results():
    if 'user_id' not in session:
        return redirect(url_for('signin'))
    
    total_votes = db.get_total_votes()
    candidate_stats = db.get_candidate_stats()
    return render_template('results.html', 
                         total_votes=total_votes,
                         candidate_stats=candidate_stats)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_tables()
    app.run(debug=True, port=5000)