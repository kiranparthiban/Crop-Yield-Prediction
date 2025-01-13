import React, { useEffect, useState } from "react";
import "./OceanAnimation.css";

const OceanAnimation = () => {
  const [bubbles, setBubbles] = useState([]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Add a new bubble to the array every 500ms
      setBubbles((prevBubbles) => [
        ...prevBubbles,
        { id: Date.now(), size: Math.random() * 50 + 10 }, // Unique ID and random size
      ]);

      // Remove bubbles that have already completed their animation
      setBubbles((prevBubbles) =>
        prevBubbles.filter((bubble) => Date.now() - bubble.id < 20000) // 10s lifetime
      );
    }, 1500);

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  return (
    <div className="ocean">
      <div className="bubbles">
        {bubbles.map((bubble) => (
          <span
            key={bubble.id}
            style={{
              width: `${bubble.size}px`,
              height: `${bubble.size}px`,
              left: `${Math.random() * 100}%`,
              animationDuration: `${Math.random() * 5 + 5}s`, // Random animation duration
            }}
          ></span>
        ))}
      </div>
      <div className="fish">
        {/* Eyes */}
        <span></span>
        <span></span>
        {/* Mouth */}
        <span></span>
        {/* Bubbles */}
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};

export default OceanAnimation;
