import { useState } from "react";
import OverlaysUI from "./overlays/OverlaysUI"; // Make sure the import path is correct
import FiltersUI from "./filters/FiltersUI";
import useFetchFilters from "./filters/Filters";

/**
* ToolsUI component that provides a user interface for various tools and overlays.
* It includes buttons for toggling drawing, undoing actions, clearing the canvas,
* selecting shapes, and applying filters.
*
* @param {function} onToggleDrawing - Function to toggle drawing mode.
* @param {function} onUndo - Function to undo the last action.
* @param {function} onClear - Function to clear the canvas.
* @param {function} onSelectShape - Function to select a shape type.
* @param {string} apiEndpoint - API endpoint for fetching filter options.
* @param {function} onFilterApply - Function to apply selected filters.
* @param {function} onToggleWeather - Function to toggle weather overlay.
* @param {function} onToggleOceanConditions - Function to toggle ocean conditions overlay.
* @param {function} onToggleTrafficHeatmaps - Function to toggle traffic heatmaps overlay.
* @param {function} onToggleEEZ - Function to toggle EEZ overlay.
* @param {boolean} showEEZState - Current state of the EEZ overlay visibility.
*
* @returns {JSX.Element} The rendered ToolsUI component.
* @description This component manages the state of the UI controls,
* including the visibility of different panels (tools, overlays, filters).
* It uses the useFetchFilters hook to fetch filter options from the API.
*/

const ToolsUI = ({
    onToggleDrawing,
    onUndo, 
    onClear, 
    onSelectShape, 
    apiEndpoint, 
    onFilterApply,
    onToggleWeather,
    onToggleOceanConditions,
    onToggleTrafficHeatmaps,
    onToggleEEZ,
    showEEZState,
    onActiveWeatherLayer,
}) => {
    const [openPanel, setOpenPanel] = useState(false);
    const { loading, error } = useFetchFilters(apiEndpoint);

    const handleToggle = (panel) => {
        setOpenPanel((prev) => (prev === panel ? null : panel));
    };

    const [showWeather, setShowWeather] = useState(false);
    const [showOcean, setShowOcean] = useState(false);
    const [showHeatmaps, setShowHeatmaps] = useState(false);
    const [activeWeatherLayer, setActiveWeatherLayer] = useState(null);


    const handleToggleWeather = (currentState, setState) => {
        setState(!currentState);
    };

    const handleToggleOceanConditions = (currentState, setState) => {
        setState(!currentState);
    };

    const handleToggleTrafficHeatmaps = (currentState, setState) => {
        setState(!currentState);
    };

    return (
        <div className="ui-controls">
            {/*Button to expand/collapse sidebars*/}
            <button onClick={() => handleToggle("tools")}>
                {openPanel === "tools" ? "Tools" : "Tools"}
            </button>

            <button onClick={() => handleToggle("overlays")}>
                {openPanel === "overlays" ? "Overlays" : "Overlays"}
            </button>

            <button onClick={() => handleToggle("filters")}>
                {openPanel === "filters" ? "Filters" : "Filters"}
            </button>

            {/* Sidebar Content */}
            {openPanel === "tools" && (
                <div className="tools-panel">
                    <h4>Zoning Tools</h4>
                    <button onClick={onToggleDrawing}>Toggle Zoning Tool</button>
                    <button onClick={onUndo}>Undo</button>
                    <button onClick={onClear}>Clear</button>
                </div>
            )}

            {/* Use the OverlaysUI component instead of hardcoded panel */}
            {openPanel === "overlays" && (
                <OverlaysUI
                    onClose={() => handleToggle(null)}
                    onToggleWeather={() => handleToggleWeather(showWeather, setShowWeather)}
                    // onToggleOceanConditions={() =>
                    //     handleToggleOceanConditions(showOcean, setShowOcean)
                    // }
                    // onToggleTrafficHeatmaps={() =>
                    //     handleToggleTrafficHeatmaps(showHeatmaps, setShowHeatmaps)
                    // }
                    onToggleEEZ={onToggleEEZ} // Pass the EEZ toggle handler
                    showEEZState={showEEZState} // Pass the current EEZ visibility state
                    onActiveWeatherLayer={onActiveWeatherLayer}
                />
            )}

            {openPanel === "filters" && (
                <div className="filter-panel">
                    <h3>Filters</h3>
                    {loading && <div>Loading...</div>}
                    {error && <div>{error}</div>}
                    {!loading && !error && (
                        <FiltersUI
                            apiEndpoint={apiEndpoint}
                            onFilterApply={onFilterApply}
                        />
                    )}
                    <button onClick={() => handleToggle(null)}>Close</button>
                </div>
            )}
        </div>
    );
};

export default ToolsUI;
