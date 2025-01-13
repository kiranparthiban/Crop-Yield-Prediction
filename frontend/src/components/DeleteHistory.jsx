
import React, { useState } from "react";

const baseUrl = "http://127.0.0.1:8000"; // Django backend


const DeleteHistory = () => {
  const [imageId, setImageId] = useState("");

  const handleDelete = async () => {
    if (!imageId) {
      alert("Please enter an Image ID.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/history/", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image_id: imageId }),
      });

      const data = await response.json();

      if (response.ok) {
        alert(`Successfully deleted history with ID: ${imageId}`);
        setImageId("");
      } else {
        alert(data.error || "Failed to delete history.");
      }
    } catch (error) {
      console.error("Error deleting history:", error);
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <div className="delete-container">
      <input
        type="number"
        placeholder="Enter Image ID"
        value={imageId}
        onChange={(e) => setImageId(e.target.value)}
        className="delete-input"
      />
      <button onClick={handleDelete} className="delete-button">
        Delete
      </button>
    </div>
  );
};

export default DeleteHistory;
