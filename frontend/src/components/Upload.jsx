import React, { useState } from "react";

const baseUrl = "http://127.0.0.1:8000/api"; // Backend base URL

const Upload = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");
  const [summary, setSummary] = useState(""); // State for storing summary
  const [previewImage, setPreviewImage] = useState(
    "placeholder.jpeg" // Path to your placeholder image
  );

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setPreviewImage(URL.createObjectURL(uploadedFile)); // Set uploaded image as preview
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select an image to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await fetch(`${baseUrl}/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setStatusMessage(
        `Uploaded successfully! Class: ${data.class_name}, Confidence: ${data.confidence}`
      );
      setSummary(data.summary); // Set the summary from the backend
      onSuccess(); // Notify App.jsx to refresh history
    } catch (error) {
      console.error("Error uploading image:", error);
      setStatusMessage("An error occurred while uploading the image.");
      setSummary(""); // Clear summary on error
    }
  };

  return (
    <div className="main-content">
      <div className="upload-container">
        <div className="upload-preview">
          <img
            src={previewImage}
            alt="Uploaded Preview"
            className="uploaded-image"
          />
        </div>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file-input"
        />
        <button className="upload-button" onClick={handleUpload}>
          Upload
        </button>
        {statusMessage && (
          <p className="status-message">{statusMessage}</p>
        )}
        {summary && (
          <div className="summary-container">
            <h4>Summary:</h4>
            <p>{summary}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
