from flask import Flask, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
import cv2
import numpy as np
import uuid
import subprocess
from werkzeug.utils import secure_filename
import pydicom
from datetime import datetime
import platform

# 初始化Flask应用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brain_mri.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'dcm', 'nii'}

# MATLAB配置（根据实际路径修改）
MATLAB_ROOT = r"D:\Matlab"  # 使用原始Windows路径
CAT12_PATH = r"D:\spm\spm12\spm12\toolbox\cat12"

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    patient_name = db.Column(db.String(255))
    check_date = db.Column(db.String(255))
    lesion_volume = db.Column(db.Float)
    tissue_stats = db.Column(db.JSON)

    def __repr__(self):
        return f'<Image {self.filename}>'

def convert_path(path):
    """处理Windows路径空格问题"""
    return f'"{path}"' if ' ' in path else path

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_dicom_to_nii(dcm_path, nii_path):
    try:
        subprocess.run([
            'dcm2niix',
            '-o', os.path.dirname(nii_path),
            '-f', os.path.basename(nii_path).replace('.nii', ''),
            dcm_path
        ], check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"DICOM转换失败: {e}")
        return False

def process_with_cat12(input_path):
    # 添加路径调试输出
    print(f"[DEBUG] 原始输入路径: {input_path}")
    input_win = convert_path(input_path.replace('/', '\\'))
    print(f"[DEBUG] 转换后路径: {input_win}")

    # 检查文件是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    try:
        output_dir = os.path.join(
            app.config['PROCESSED_FOLDER'],
            datetime.now().strftime("%Y%m%d%H%M%S")
        )
        os.makedirs(output_dir, exist_ok=True)

        # 转换路径格式并处理空格
        input_win = convert_path(input_path.replace('/', '\\'))
        output_win = convert_path(output_dir.replace('/', '\\'))

        # 构建MATLAB命令
        matlab_cmd = f'''
        addpath('{CAT12_PATH}');
        cat12_batch_processing({input_win}, {output_win});
        exit;
        '''

        # 执行MATLAB命令
        subprocess.run(
            [
                os.path.join(MATLAB_ROOT, 'bin', 'matlab.exe'),
                '-batch',
                matlab_cmd
            ],
            check=True,
            shell=True
        )

        # 解析结果（需要根据实际输出实现）
        stats = {
            'lesion_volume': 15.7,
            'gray_matter': 63.3,
            'white_matter': 34.1
        }
        
        return {
            'status': 'success',
            'output_dir': output_dir,
            'stats': stats
        }
    except subprocess.CalledProcessError as e:
        return {
            'status': 'error',
            'message': f"处理失败: {str(e)}"
        }

@app.route('/api/process', methods=['POST'])
def process_mri():
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '无效文件名'}), 400

    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.{original_ext}")
        file.save(original_path)

        # DICOM转NIfTI
        if original_ext == 'dcm':
            nii_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}.nii")
            if not convert_dicom_to_nii(original_path, nii_path):
                return jsonify({'error': 'DICOM转换失败'}), 500
            input_path = nii_path
        else:
            input_path = original_path

        result = process_with_cat12(input_path)
        if result['status'] != 'success':
            return jsonify({'error': result['message']}), 500

        new_image = Image(
            filename=file.filename,
            patient_name=request.form.get('patient_name', '未知'),
            check_date=request.form.get('check_date', datetime.now().strftime("%Y-%m-%d")),
            lesion_volume=result['stats']['lesion_volume'],
            tissue_stats=result['stats']
        )
        db.session.add(new_image)
        db.session.commit()

        return jsonify({
            'message': '处理成功',
            'results': result['stats'],
            'processed_images': [
                os.path.join(result['output_dir'], f)
                for f in os.listdir(result['output_dir'])
                if f.endswith(('.nii', '.png', '.jpg'))
            ]
        })

    return jsonify({'error': '文件类型不支持'}), 400

@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')