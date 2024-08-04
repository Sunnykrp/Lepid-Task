import React from 'react';
import './App.css';
import FileUpload from './components/FileUpload';

const App = () => {
  return (
    <div className="app-container">
      <h1>Document Summarization App</h1>
      <FileUpload />
    </div>
  );
};

export default App;
