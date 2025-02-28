import React from "react";

export default function BoatIcon({
  type = "cargo", // Default vessel type
  size = 100, // Default size
}) {
  // Define color schemes for different vessel types
  const vesselColors = {
    cargo: "#6B8E23", // Olive green
    fishing: "#8B4513", // Brown
    tankers: "#CD5C5C", // Indian red
    highSpeedCraft: "#4682B4", // Steel blue
  };

  // Get the color based on the vessel type
  const getVesselColor = () => {
    // Get the base color
    const baseColor = vesselColors[type] || vesselColors.cargo;
    // Return the color with 50% opacity
    return baseColor + "90"; // 80 in hex is 50% opacity
  };
  
  // Calculate the points for a simple angle shape like <
  const getAnglePoints = () => {
    // Simple angle shape (like <)
    return `
      0,${size/2}
      ${size},0 
      ${size},${size}
    `;
  };

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox={`0 0 ${size} ${size}`}
      width={size}
      height={size}
    >
      {/* Simple angle shape (like <) */}
      <polygon
        points={getAnglePoints()}
        fill={getVesselColor()}
        stroke={vesselColors[type] || vesselColors.cargo}
        strokeWidth="3" // Bolder border
        strokeLinejoin="round" // Rounded corners on the stroke
      />
    </svg>
  );
}