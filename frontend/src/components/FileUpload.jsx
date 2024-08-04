import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
    setSummary('');  // Ensure summary is cleared on file change
    setMessage('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (uploadResponse.data.message === 'File uploaded successfully') {
        setMessage('File is uploaded successfully.');
        setSummary('');  // Ensure summary is cleared after successful upload
        const summarizeResponse = await axios.post('http://localhost:5000/summarize', {
          fileName: uploadResponse.data.fileName,
        });
        setSummary(summarizeResponse.data.summary);
        setError('');
      } else {
        setMessage('Failed to upload file.');
        setSummary('');
      }
    } catch (error) {
      console.error('Error uploading or summarizing the file:', error);
      setMessage('Failed to upload file.');
      setError('An error occurred while uploading or summarizing the file.');
    }
  };

  return (
    <div className="file-upload-container">
      <h2>Upload a Document for Summarization</h2>
      <input type="file" onChange={handleFileChange} className="file-input" />
      <button onClick={handleUpload} className="upload-button">Upload and Summarize</button>
      {message && <p className="message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
      {summary && (
        <div className="summary-container">
          <h3>Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
