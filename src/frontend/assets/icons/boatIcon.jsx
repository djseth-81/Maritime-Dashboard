import React from "react";

export default function BoatIcon({
  type = "cargo", // Default to cargo vessel
  hullColor = "#8B4513", // Default hull color (brown)
  cabinColor = "#A0522D", // Default cabin color (darker brown)
  windowColor = "#87CEEB", // Default window color (light blue)
  mastColor = "#654321", // Default mast color (dark brown)
  sailColor = "#FFFFFF", // Default sail color (white)
}) {
  // Define color schemes based on vessel type
  const colors = {
    cargo: {
      hullColor: "#6B8E23", // Olive brown for cargo hull
      cabinColor: "#556B2F", // Dark olive for cargo cabin
      windowColor: "#87CEEB", // Light blue windows
      mastColor: "#654321", // Dark brown mast
      sailColor: "#FFFFFF", // White sail
    },
    fishing: {
      hullColor: "#A0522D", // Coffee brown for fishing hull
      cabinColor: "#8B0000", // Dark red for fishing cabin
      windowColor: "#87CEEB", // Light blue windows
      mastColor: "#654321", // Dark brown mast
      sailColor: "#FFFFFF", // White sail
    },
  };

  // Use the color scheme based on the vessel type
  const vesselColors = type === "cargo" ? colors.cargo : colors.fishing;

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 200"
      width="200"
      height="200"
    >
      {/* Hull */}
      <path
        d="M20 150 Q100 200 180 150 L180 170 Q100 220 20 170 Z"
        fill={vesselColors.hullColor || hullColor}
      />

      {/* Cabin */}
      <rect x="70" y="100" width="60" height="50" fill={vesselColors.cabinColor || cabinColor} />

      {/* Windows */}
      <circle cx="85" cy="125" r="5" fill={vesselColors.windowColor || windowColor} />
      <circle cx="115" cy="125" r="5" fill={vesselColors.windowColor || windowColor} />

      {/* Mast */}
      <rect x="97" y="50" width="6" height="100" fill={vesselColors.mastColor || mastColor} />

      {/* Sail */}
      <path
        d="M100 50 L150 100 L100 100 Z"
        fill={vesselColors.sailColor || sailColor}
      />
      <path
        d="M100 50 L50 100 L100 100 Z"
        fill={vesselColors.sailColor || sailColor}
      />
    </svg>
  );
}