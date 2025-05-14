import { useState } from "react";
import WeatherOverlay from "./WeatherOverlay";

/**
 * OverlaysUI component
 * @param {Object} props - Component props.
 * @param {Function} props.onClose - Callback function to close the overlays UI.
 * @param {Function} props.onToggleWeather - Callback function to toggle weather overlay.
 * @param {Function} props.onToggleOceanConditions - Callback function to toggle ocean conditions overlay.
 * @param {Function} props.onToggleTrafficHeatmaps - Callback function to toggle traffic heatmaps overlay.
 * @param {Function} props.onToggleEEZ - Callback function to toggle EEZ overlay.
 * @param {boolean} props.showEEZState - Current state of the EEZ overlay visibility.
 * @returns {JSX.Element} - Rendered component.
 * @description This component provides a user interface for managing overlays on the map, including weather, ocean conditions, and traffic heatmaps.
 */
const OverlaysUI = ({
  onClose,
  onToggleWeather,
  onToggleOceanConditions,
  onToggleTrafficHeatmaps,
  onToggleEEZ,
  showEEZState,
  onActiveWeatherLayer,
}) => {
  const [showWeather, setShowWeather] = useState(false);
  const [showOceanConditions, setShowOceanConditions] = useState(false);
  const [showTrafficHeatmaps, setShowTrafficHeatmaps] = useState(false);

  const handleWeatherToggle = () => {
    setShowWeather(!showWeather);
    console.log("Weather Overlay Toggled");
  };

  return (
    <div className="overlay-panel">
      <div className="menu-header">Overlays</div>
      <button onClick={handleWeatherToggle}>
        {showWeather ? "Hide Weather Overlay" : "Show Weather Overlay"}
      </button>

      <button onClick={() => {
        // console.log("EEZ button clicked in OverlaysUI");
        onToggleEEZ();
      }}>
        {showEEZState ? "Hide EEZ" : "Show EEZ"}
      </button>
      <button onClick={onClose}>Close</button>
      {showWeather && (
        <div className="overlay-panel" style={{ margin: "50px" }}>
          <WeatherOverlay onActiveWeatherLayer={onActiveWeatherLayer} />
          <button onClick={handleWeatherToggle}>Close</button>
        </div>
      )}
    </div>
  );
};

export default OverlaysUI;
