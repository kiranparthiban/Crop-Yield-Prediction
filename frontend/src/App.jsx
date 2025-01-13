import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios"; // For API calls
import Upload from "./components/Upload";
import History from "./components/History";
import DeleteHistory from "./components/DeleteHistory";
import OceanAnimation from "./components/OceanAnimation";
import LoginPage from "./components/LoginPage";
import SignupPage from "./components/SignupPage";
import "./App.css";

const App = () => {
  const [showHistory, setShowHistory] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [historyTrigger, setHistoryTrigger] = useState(0); // Trigger for refreshing history

  const handleUploadSuccess = () => {
    setHistoryTrigger((prev) => prev + 1); // Increment trigger to refresh history
  };

  return (
    <Router>
      <div className="app">
        {/* Ocean Animation */}
        <OceanAnimation />

        {/* Routes */}
        <Routes>
          {/* Base URL redirects to login */}
          <Route path="/" element={<Navigate to="/login" />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/app"
            element={
              <AppContent
                showHistory={showHistory}
                setShowHistory={setShowHistory}
                showDelete={showDelete}
                setShowDelete={setShowDelete}
                historyTrigger={historyTrigger}
                handleUploadSuccess={handleUploadSuccess}
              />
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

const AppContent = ({
  showHistory,
  setShowHistory,
  showDelete,
  setShowDelete,
  historyTrigger,
  handleUploadSuccess,
}) => {
  const [selectedModel, setSelectedModel] = useState(""); // State to store selected model
  const [modelMessage, setModelMessage] = useState(""); // Message for success/error
  const [showModelSelection, setShowModelSelection] = useState(true); // Control visibility of model selection

  // Handle model selection
  const handleModelChange = (e) => {
    const model = e.target.value;
    setSelectedModel(model);
    setModelMessage(`Model "${model}" selected!`); // Display the selected model
    setTimeout(() => {
      setModelMessage("");
    }, 1000); // Clear message after 1 second
  };

  // Handle upload success
  const handleUpload = () => {
    if (!selectedModel) {
      setModelMessage("Please select a model before uploading!");
      setTimeout(() => {
        setModelMessage("");
      }, 1000);
      return;
    }
    setShowModelSelection(false); // Hide model selection after upload
    handleUploadSuccess(); // Trigger parent upload success logic
  };

  return (
    <>
      {/* Top Buttons */}
      <div className="top-buttons">
        <button
          className="view-history-button"
          onClick={() => setShowHistory(true)}
        >
          View Classification History
        </button>
        <button
          className="delete-history-button"
          onClick={() => setShowDelete(!showDelete)}
        >
          {showDelete ? "Close Delete" : "Delete History"}
        </button>
      </div>

      {/* Model Selection */}
      {showModelSelection && (
        <div className="model-selection">
          <label htmlFor="model-dropdown">Choose a Model:</label>
          <select
            id="model-dropdown"
            value={selectedModel}
            onChange={handleModelChange}
          >
            <option value="">Select a model</option>
            <option value="resnet">ResNet50</option>
            <option value="efficientnet">EfficientNet</option>
            <option value="mobilenet">MobileNet</option>
          </select>
          {modelMessage && <p className="model-message">{modelMessage}</p>}
        </div>
      )}

      {/* Sliding Sidebar */}
      <div className={`history-sidebar ${showHistory ? "open" : ""}`}>
        <button
          className="close-sidebar-button"
          onClick={() => setShowHistory(false)}
        >
          &times;
        </button>
        <History refreshTrigger={historyTrigger} />
      </div>

      {/* Main Content */}
      <div className="main-content">
        <Upload onSuccess={handleUpload} selectedModel={selectedModel} />
        {showDelete && <DeleteHistory />}
      </div>
    </>
  );
};

export default App;
