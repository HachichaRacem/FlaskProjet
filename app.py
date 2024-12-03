from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
from PIL import Image
import numpy as np

app = Flask (__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model = tf.keras.models.load_model('./model.h5')
print("SHAPE: ", model.input_shape)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'rdv_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-appointment', methods=['POST'])
def add_appointment():
    patient_name = request.form['patient_name'] 
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    phone_number = request.form['phone_number']

    prediction_result = None
    filename = None
    document = request.files['document']
    categories = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
    if document.filename != '':
        filename = secure_filename(document.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        document.save(file_path)

        image = Image.open(file_path).resize((100, 100))
        image = image.convert("RGB")
        image = (np.array(image)) / 255.0
        image = np.expand_dims (image, axis=0)
        prediction = model.predict(image)
        predicted_class = np.argmax(prediction)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO classifications (filename, prediction) VALUES (%s, %s)",
            (filename, categories[predicted_class])
        )
        conn.commit()
        conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rdv (patient_name, phone_number, appointment_date, appointment_time, filename)
            VALUES (%s, %s, %s, %s, %s)
        ''', (patient_name, phone_number, appointment_date, appointment_time, filename))
        conn.commit()
        conn.close()
    else:
        print("filename is null")
    return redirect(url_for('liste_rdv'))

@app.route('/liste-rdv')
def liste_rdv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT a.ID, a.patient_name, a.phone_number, a.appointment_date, a.appointment_time, p.prediction FROM rdv a JOIN classifications p ON a.filename = p.filename")
    rdv = cursor.fetchall()
    conn.close()
    return render_template('liste_rdv.html', appointments=rdv)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)