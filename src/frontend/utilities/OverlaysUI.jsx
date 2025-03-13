import { useState } from "react";

const OverlaysUI = ({ onClose, onToggleWeather, onToggleOceanConditions, onToggleTrafficHeatmaps }) => {
    const [showWeather, setShowWeather] = useState(false);
    const [showOceanConditions, setShowOceanConditions] = useState(false);
    const [showTrafficHeatmaps, setShowTrafficHeatmaps] = useState(false);

    const handleWeatherToggle = () => {
        console.log("Weather Overlay Toggled");
    };

    const handleOceanConditionToggle = () => {
        console.log("Ocean Conditions Toggled");
    };

    const handleTrafficToggle = () => {
        console.log("Traffic Heatmaps Toggled");
    };

    return (
        // placeholder values and buttons
        <div className="overlay-panel">
            <h3>Overlays</h3>
            <button onClick={onClose}>Close</button>
            <button onClick={handleWeatherToggle}>
                {showWeather ? "Hide Weather Overlay" : "Show Weather Overlay"}
            </button>
            <button onClick={handleOceanConditionToggle}>
                {showOceanConditions ? "Hide Ocean Conditions" : "Show Ocean Conditions"}
            </button>
            <button onClick={handleTrafficToggle}>
                {showTrafficHeatmaps ? "Hide Traffic Heatmaps" : "Show Traffic Heatmaps"}
            </button>
        </div>
    );
};

export default OverlaysUI