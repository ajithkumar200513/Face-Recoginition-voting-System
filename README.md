# 🗳️ Smart Online Voting System

A Smart Online Voting System using facial recognition to authenticate users and ensure secure, fair voting. This project is developed using Python, OpenCV, Scikit-learn, and leverages the K-Nearest Neighbors (KNN) machine learning algorithm for face recognition. It also provides real-time visual statistical results such as bar charts and pie charts to display the ongoing election outcome.
![Uploading what-is-facial-recognition-1-q75.jpg…]()

## ✅ Features

- 🔐 **Face Recognition Authentication** using KNN algorithm.
- 🗳️ **Secure Voting System** – one person, one vote.
- 📊 **Real-Time Statistical Results** – includes pie charts, bar graphs, and vote percentages.
- 💾 Voter face data management and training set generation.
- 🧠 Uses **Scikit-learn** for KNN model training.
- 👁️ Built with **OpenCV** for image processing.

---

## 💻 Technologies Used

- **Python 3**
- **OpenCV**
- **Scikit-learn**
- **Matplotlib** / **Seaborn** (for plotting)
- **NumPy**
- **Tkinter** (optional for GUI)

---

## 🚀 Getting Started


---

## 🚀 How It Works

### 1. Face Registration
Run `face_capture.py` to collect multiple facial images per voter.

### 2. Model Training
Use `train_model.py` to train the KNN classifier using the collected dataset.

### 3. Voting
Run `recognize_and_vote.py`. The system matches the user's face with the trained model and allows them to vote once if verified.

### 4. Results
Run `result_display.py` to generate bar graphs, pie charts, and vote statistics.

---

## ▶️ How to Run the App

Make sure all dependencies are installed. You can run the main app (if `app.py` combines all phases or includes a GUI) using the following command:

```bash
python app.py


### 📦 Prerequisites

Make sure you have Python 3.x and pip installed.

```bash
pip install opencv-python scikit-learn numpy matplotlib
