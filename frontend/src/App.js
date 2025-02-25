import React, { useState } from 'react';
import axios from 'axios';

function App() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [scale, setScale] = useState(1);
    const [processedImage, setProcessedImage] = useState(null);

    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (selectedFile) {
            const formData = new FormData();
            formData.append('image', selectedFile);
            try {
                const response = await axios.post('http://backend:5000/upload', formData, {
                    onUploadProgress: (e) => {
                        if (e.lengthComputable) {
                            const percentComplete = (e.loaded / e.total) * 100;
                            setUploadProgress(percentComplete);
                        }
                    },
                });
                setProcessedImage(response.data.processed_image);
                console.log('Upload successful', response.data);
            } catch (error) {
                console.error('Upload failed', error);
            }
        }
    };

    const handleZoomIn = () => {
        setScale(scale + 0.1);
    };

    const handleZoomOut = () => {
        if (scale > 0.1) {
            setScale(scale - 0.1);
        }
    };

    return (
        <div>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>
            <div>Upload Progress: {uploadProgress}%</div>
            {selectedFile && (
                <div>
                    <button onClick={handleZoomIn}>Zoom In</button>
                    <button onClick={handleZoomOut}>Zoom Out</button>
                    <img
                        src={URL.createObjectURL(selectedFile)}
                        alt="Uploaded MRI"
                        style={{ width: `300px`, transform: `scale(${scale})` }}
                    />
                </div>
            )}
            {processedImage && (
                <div>
                    <h3>Processed Image</h3>
                    <img
                        src={`http://backend:5000/uploads/${processedImage}`}
                        alt="Processed MRI"
                        style={{ width: `300px`, transform: `scale(${scale})` }}
                    />
                </div>
            )}
        </div>
    );
}

export default App;