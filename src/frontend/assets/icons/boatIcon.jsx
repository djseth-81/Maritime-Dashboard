import React from "react";

export default function BoatIcon({
  type = "OTHER", // Default vessel type
  size = 100, // Default size
  heading = 0, // Default orientation
}) {
  // Define color schemes for different vessel types
  // Could we use the vessel types from get_filters() to populate the keys here?
  const vesselColors = {
    CARGO: "#6B8E23", // Olive green
    FISHING: "#8B4513", // Brown
    TANKER: "#FA6B05", // Indian red
    TUG: "#F9C256", // Gold
    RECREATIONAL: "#D31EFF", // Magenta
    PASSENGER: "#4682B4", // Steel blue
    OTHER: "#CD5C5C" //  Indian red
  };

  // Get the color based on the vessel type
  const getVesselColor = () => {
    // Get the base color
    const baseColor = vesselColors[type] || vesselColors.cargo;
    // Return the color with 50% opacity
    return baseColor + "B3"; // 80 in hex is 50% opacity
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
      transform = {`rotate(${heading} 0 0)`}
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
