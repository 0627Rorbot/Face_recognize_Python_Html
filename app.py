from flask import Flask, render_template, Response, request, redirect, flash, url_for, session
from flask_pymongo import PyMongo
import os
import cv2
import dlib

app = Flask(__name__)
app.config['SECRET_KEY']="1234"
app.config['MONGO_URI']="mongodb+srv://2100090162:manigaddam@deepsheild.kzgpo9p.mongodb.net/facerecognitionDB"  
mongo=PyMongo(app)
detector = dlib.get_frontal_face_detector()

def detect_faces(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray_frame)
    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return frame


@app.route('/process_image', methods=['POST'])
def process_image():
    video_file = request.files['video']
    video_file.save('static/uploads/video.mp4')  # Save uploaded video
    return redirect(url_for('detection'))

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/videodrop')
def videodrop():
    return render_template('videodrop.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

def gen_frames():
    cap = cv2.VideoCapture('static/uploads/video.mp4')
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        else:
            frame = detect_faces(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_data = mongo.db.users.find_one({'email': email, 'password': password})
        print(user_data)

        if user_data:
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)
    
    

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user_data = {
            'firstname': request.form.get('firstname'),
            'lastname': request.form.get('lastname'),
            'email': request.form.get('email'),
            'password': request.form.get('password')
        }
        mongo.db.users.insert_one(user_data)
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
