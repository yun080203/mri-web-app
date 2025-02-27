// 导入 React 库中的 useState 钩子，用于在函数组件中添加状态管理
import React, { useState } from 'react';
// 导入 axios 库，用于发送 HTTP 请求
import axios from 'axios';

// 定义一个名为 App 的函数组件
function App() {
    // 使用 useState 钩子创建状态变量 selectedFile，用于存储用户选择的文件
    // 初始值为 null，表示还没有选择文件
    const [selectedFile, setSelectedFile] = useState(null);
    // 使用 useState 钩子创建状态变量 uploadProgress，用于存储文件上传的进度
    // 初始值为 0，表示还没有开始上传
    const [uploadProgress, setUploadProgress] = useState(0);
    // 使用 useState 钩子创建状态变量 scale，用于控制图片的缩放比例
    // 初始值为 1，表示图片正常大小
    const [scale, setScale] = useState(1);
    // 使用 useState 钩子创建状态变量 processedImage，用于存储处理后的图片文件名
    // 初始值为 null，表示还没有处理后的图片
    const [processedImage, setProcessedImage] = useState(null);
    // 新增：定义 errorMessage 状态变量和对应的更新函数
    const [errorMessage, setErrorMessage] = useState('');

    // 定义一个处理文件选择事件的函数
    const handleFileChange = (e) => {
        // 当用户选择文件时，将选择的第一个文件存储到 selectedFile 状态中
        setSelectedFile(e.target.files[0]);
    };

    // 定义一个处理文件上传的异步函数
    const handleUpload = async () => {
        // 检查用户是否选择了文件
        if (selectedFile) {
            // 创建一个 FormData 对象，用于将文件数据以表单形式发送
            const formData = new FormData();
            // 将选择的文件添加到 FormData 对象中，键名为 'image'
            formData.append('image', selectedFile);
            try {
                // 使用 axios 发送 POST 请求到指定的后端地址 'http://backend:5000/upload'
                // 并传递 FormData 对象作为请求体
                const response = await axios.post('http://backend:5000/upload', formData, {
                    // 监听上传进度事件
                    onUploadProgress: (e) => {
                        // 检查上传进度是否可计算
                        if (e.lengthComputable) {
                            // 计算上传的百分比
                            const percentComplete = (e.loaded / e.total) * 100;
                            // 更新 uploadProgress 状态，显示上传进度
                            setUploadProgress(percentComplete);
                        }
                    },
                });
                // 将后端返回的处理后的图片文件名存储到 processedImage 状态中
                setProcessedImage(response.data.processed_image);
                // 在控制台打印上传成功的信息和后端返回的数据
                console.log('Upload successful', response.data);
                setErrorMessage('');
            } catch (error) {
                // 如果上传过程中出现错误，在控制台打印上传失败的信息和错误对象
                console.error('Upload failed', error);
                setErrorMessage('上传失败，请稍后重试。');
            }
        }
    };

    // 定义一个处理放大图片的函数
    const handleZoomIn = () => {
        // 每次点击放大按钮，将缩放比例增加 0.1
        setScale(scale + 0.1);
    };

    // 定义一个处理缩小图片的函数
    const handleZoomOut = () => {
        // 检查缩放比例是否大于 0.1，避免缩小到太小
        if (scale > 0.1) {
            // 每次点击缩小按钮，将缩放比例减少 0.1
            setScale(scale - 0.1);
        }
    };

    // 返回 JSX 元素，用于渲染组件的 UI
    return (
        <div>
            {/* 创建一个文件输入框，当用户选择文件时触发 handleFileChange 函数 */}
            <input type="file" onChange={handleFileChange} />
            {/* 创建一个上传按钮，点击时触发 handleUpload 函数 */}
            <button onClick={handleUpload}>Upload</button>
            {/* 显示文件上传的进度 */}
            <div>Upload Progress: {uploadProgress}%</div>
            {/* 如果用户选择了文件，显示缩放按钮和上传的图片 */}
            {selectedFile && (
                <div>
                    {/* 放大按钮，点击时触发 handleZoomIn 函数 */}
                    <button onClick={handleZoomIn}>Zoom In</button>
                    {/* 缩小按钮，点击时触发 handleZoomOut 函数 */}
                    <button onClick={handleZoomOut}>Zoom Out</button>
                    {/* 显示上传的图片，使用 URL.createObjectURL 方法创建临时 URL */}
                    <img
                        src={URL.createObjectURL(selectedFile)}
                        alt="Uploaded MRI"
                        /* 设置图片的宽度为 300px，并根据 scale 状态进行缩放 */
                        style={{ width: `300px`, transform: `scale(${scale})` }}
                    />
                </div>
            )}
            {/* 如果处理后的图片文件名存在，显示处理后的图片 */}
            {processedImage && (
                <div>
                    <h3>Processed Image</h3>
                    {/* 显示处理后的图片，从后端地址获取图片 */}
                    <img
                        src={`http://backend:5000/uploads/${processedImage}`}
                        alt="Processed MRI"
                        // 设置图片的宽度为 300px，并根据 scale 状态进行缩放
                        style={{ width: `300px`, transform: `scale(${scale})` }}
                    />
                </div>
            )}
            {/* 新增：如果有错误信息，显示错误信息 */}
            {errorMessage && <div style={{ color: 'red' }}>{errorMessage}</div>}
        </div>
    );
}

// 导出 App 组件，以便在其他文件中使用
export default App;