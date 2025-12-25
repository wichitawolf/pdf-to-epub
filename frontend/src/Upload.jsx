import React, { useState } from 'react';
import axios from 'axios';

const Upload = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post("http://127.0.0.1:8000/convert", formData, {
                // CRITICAL: This tells axios to handle binary data
                responseType: 'blob', 
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setProgress(percentCompleted);
                }
            });

            // Create a link to download the binary blob
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', file.name.replace(".pdf", ".epub"));
            document.body.appendChild(link);
            link.click();
            link.remove();
            
            setProgress(0);
        } catch (error) {
            console.error("Download Error:", error);
            alert("The server returned an error. Check the Backend console.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="upload-container">
            <input type="file" onChange={(e) => setFile(e.target.files[0])} accept=".pdf" />
            <button onClick={handleUpload} disabled={loading}>
                {loading ? `Processing (${progress}%)` : "Convert PDF"}
            </button>
            {loading && <div className="progress-bar" style={{width: `${progress}%`, height: '4px', background: 'blue'}} />}
        </div>
    );
};

export default Upload;