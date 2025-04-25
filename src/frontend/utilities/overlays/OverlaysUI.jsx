import { useState } from "react";

/**
 * OverlaysUI component
 * @param {Object} props - Component props.
 * @param {Function} props.onClose - Callback function to close the overlays UI.
 * @param {Function} props.onToggleWeather - Callback function to toggle weather overlay.
 * @param {Function} props.onToggleOceanConditions - Callback function to toggle ocean conditions overlay.
 * @param {Function} props.onToggleTrafficHeatmaps - Callback function to toggle traffic heatmaps overlay.
 * @param {Function} props.onToggleEEZ - Callback function to toggle EEZ overlay.
 * @returns {JSX.Element} - Rendered component.
 * @description This component provides a user interface for managing overlays on the map, including weather, ocean conditions, and traffic heatmaps.
 */
const OverlaysUI = ({ onClose, onToggleWeather, onToggleOceanConditions, onToggleTrafficHeatmaps, onToggleEEZ, showEEZState }) => {
    const [showWeather, setShowWeather] = useState(false);
    const [showOceanConditions, setShowOceanConditions] = useState(false);
    const [showTrafficHeatmaps, setShowTrafficHeatmaps] = useState(false);
    const [showEEZ, setShowEEZ] = useState(showEEZState || false);

    const handleWeatherToggle = () => {
        console.log("Weather Overlay Toggled");
    };

    const handleOceanConditionToggle = () => {
        console.log("Ocean Conditions Toggled");
    };

    const handleTrafficToggle = () => {
        console.log("Traffic Heatmaps Toggled");
    };

    const handleEEZToggle = () => {
        setShowEEZ(!showEEZ);
        if (onToggleEEZ) onToggleEEZ();
    };

    return (
        // placeholder values and buttons
        <div className="overlay-panel">
            <h3>Overlays</h3>
            <button onClick={handleWeatherToggle}>
                {showWeather ? "Hide Weather Overlay" : "Show Weather Overlay"}
            </button>
            <button onClick={handleOceanConditionToggle}>
                {showOceanConditions ? "Hide Ocean Conditions" : "Show Ocean Conditions"}
            </button>
            <button onClick={handleTrafficToggle}>
                {showTrafficHeatmaps ? "Hide Traffic Heatmaps" : "Show Traffic Heatmaps"}
            </button>
            <button onClick={handleEEZToggle}>
                {showEEZ ? "Hide EEZ" : "Show EEZ"}
            </button>
            <button onClick={onClose}>Close</button>
        </div>
    );
};

export default OverlaysUI;