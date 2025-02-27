# 从 flask 库中导入 Flask 类、request 对象和 jsonify 函数
# Flask 类用于创建 Flask 应用实例
# request 对象用于处理客户端发送的请求
# jsonify 函数用于将 Python 字典或列表转换为 JSON 响应
from flask import Flask, request, jsonify
# 导入 os 模块，用于与操作系统进行交互，例如文件和目录操作
import os
# 从 flask_sqlalchemy 库中导入 SQLAlchemy 类，用于简化 Flask 应用与数据库的交互
from flask_sqlalchemy import SQLAlchemy
# 导入 OpenCV 库，用于计算机视觉任务，如图像处理
import cv2
# 导入 NumPy 库，用于处理多维数组和矩阵，在图像处理中经常使用
import numpy as np

# 创建一个 Flask 应用实例，__name__ 是 Python 中的一个特殊变量，表示当前模块的名称
app = Flask(__name__)
# 配置 SQLAlchemy 的数据库连接 URI，使用 SQLite 数据库，数据库文件名为 brain_mri.db
# sqlite:/// 是 SQLite 数据库的 URI 前缀
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brain_mri.db'
# 初始化 SQLAlchemy 数据库对象，将其与 Flask 应用实例关联
db = SQLAlchemy(app)

# 定义一个数据库模型类 Image，继承自 db.Model，用于表示数据库中的图像记录
class Image(db.Model):
    # 定义一个整数类型的列 id，作为主键，用于唯一标识每条记录
    id = db.Column(db.Integer, primary_key=True)
    # 定义一个字符串类型的列 filename，最大长度为 255，用于存储上传图像的文件名
    filename = db.Column(db.String(255))
    # 定义一个字符串类型的列 patient_name，最大长度为 255，用于存储患者的姓名
    patient_name = db.Column(db.String(255))
    # 定义一个字符串类型的列 check_date，最大长度为 255，用于存储检查日期
    check_date = db.Column(db.String(255))

    def __repr__(self):
        # 定义对象的字符串表示形式，方便调试和日志记录
        # 当打印 Image 对象时，会显示类似 <Image example.jpg> 的信息
        return f'<Image {self.filename}>'

# 定义上传文件的存储文件夹名为 'uploads'
UPLOAD_FOLDER = 'uploads'
# 检查指定的上传文件夹是否存在
if not os.path.exists(UPLOAD_FOLDER):
    # 如果文件夹不存在，则创建该文件夹
    os.makedirs(UPLOAD_FOLDER)

# 定义一个在应用第一次请求之前执行的函数
# 该函数的作用是确保数据库中的所有表都已创建
@app.before_request
def create_tables():
    # 调用 SQLAlchemy 的 create_all 方法，根据定义的模型类创建数据库表
    db.create_all()

# 定义一个图像处理函数，接受图像文件的路径作为输入参数
def process_image(image_path):
    # 使用 OpenCV 的 imread 函数读取指定路径的图像
    image = cv2.imread(image_path)
    # 对读取的彩色图像进行去噪处理
    # cv2.fastNlMeansDenoisingColored 是 OpenCV 提供的快速非局部均值去噪算法
    # 这里的参数 10, 10, 7, 21 是算法的一些配置参数
    denoised_image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    # 将去噪后的图像从 BGR 颜色空间转换为 LAB 颜色空间
    # LAB 颜色空间更适合进行对比度增强操作
    lab = cv2.cvtColor(denoised_image, cv2.COLOR_BGR2LAB)
    # 将 LAB 图像分离为 L、a、b 三个通道
    # L 通道表示亮度，a 和 b 通道表示颜色信息
    l, a, b = cv2.split(lab)
    # 创建一个对比度受限的自适应直方图均衡化（CLAHE）对象
    # clipLimit=3.0 表示对比度限制为 3.0，tileGridSize=(8, 8) 表示将图像分割为 8x8 的小块进行处理
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    # 对 L 通道应用 CLAHE 进行对比度增强
    cl = clahe.apply(l)
    # 将处理后的 L 通道与原始的 a、b 通道合并，重新组成 LAB 图像
    enhanced_image = cv2.merge((cl, a, b))
    # 将增强后的 LAB 图像转换回 BGR 颜色空间，以便后续存储和显示
    enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_LAB2BGR)
    # 返回处理后的图像
    return enhanced_image

# 定义一个路由，当客户端向 /upload 发送 POST 请求时，会调用该函数进行处理
@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查请求中是否包含名为 'image' 的文件
    if 'image' not in request.files:
        # 如果请求中没有文件，返回一个包含错误信息的 JSON 响应，状态码为 400 表示错误请求
        return jsonify({'error': 'No file uploaded'}), 400

    # 从请求中获取名为 'image' 的文件对象
    file = request.files['image']
    # 从请求的表单数据中获取患者姓名
    patient_name = request.form.get('patient_name')
    # 从请求的表单数据中获取检查日期
    check_date = request.form.get('check_date')
    # 检查文件对象是否存在
    if file:
        # 获取上传文件的原始文件名
        filename = file.filename
        # 构建文件的保存路径，将文件名与上传文件夹路径拼接
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        # 将上传的文件保存到指定路径
        file.save(file_path)

        # 调用 process_image 函数对保存的图像进行处理
        processed_image = process_image(file_path)
        # 生成处理后图像的文件名，在原文件名前加上 'processed_' 前缀
        processed_filename = f"processed_{filename}"
        # 使用 OpenCV 的 imwrite 函数将处理后的图像保存到上传文件夹中
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, processed_filename), processed_image)

        # 创建一个新的 Image 模型对象，将文件名、患者姓名和检查日期作为参数传入
        new_image = Image(filename=filename, patient_name=patient_name, check_date=check_date)
        # 将新的 Image 对象添加到数据库会话中
        db.session.add(new_image)
        # 提交数据库会话，将新的记录保存到数据库中
        db.session.commit()

        # 返回一个包含成功信息的 JSON 响应，包含原始图像文件名和处理后图像文件名
        return jsonify({
            'message': 'File uploaded and processed successfully',
            'original_image': filename,
            'processed_image': processed_filename
        })
    # 如果文件对象不存在，返回一个包含错误信息的 JSON 响应，状态码为 400 表示错误请求
    return jsonify({'error': 'No file provided'}), 400

# 当该脚本作为主程序运行时，执行以下代码
if __name__ == '__main__':
    # 以调试模式启动 Flask 应用
    # debug=True 表示开启调试模式，方便开发过程中调试代码
    # host='0.0.0.0' 表示应用可以接受来自任何网络接口的请求
    app.run(debug=True, host='0.0.0.0')