from flask import Flask, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
import cv2
import numpy as np

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brain_mri.db'
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    patient_name = db.Column(db.String(255))
    check_date = db.Column(db.String(255))

    def __repr__(self):
        return f'<Image {self.filename}>'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.before_first_request
def create_tables():
    db.create_all()

def process_image(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    # 去噪
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    # 增强对比度
    lab = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_image = cv2.merge((cl, a, b))
    enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_LAB2BGR)
    return enhanced_image

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['image']
    patient_name = request.form.get('patient_name')
    check_date = request.form.get('check_date')
    if file:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        processed_image = process_image(os.path.join(UPLOAD_FOLDER, filename))
        processed_filename = f"processed_{filename}"
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, processed_filename), processed_image)
        new_image = Image(filename=filename, patient_name=patient_name, check_date=check_date)
        db.session.add(new_image)
        db.session.commit()
        return jsonify({
            'message': 'File uploaded and processed successfully',
            'original_image': filename,
            'processed_image': processed_filename
        })
    return 'No file provided'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')