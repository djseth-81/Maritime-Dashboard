/*
  TODO: Add Filters.jsx and Overlays.jsx
  -> Filters: Ship types
        -> Vessel types
        -> Country of origin
        -> 
  -> Overlays: Weather, ocean conditions, exclusion zones, traffic heatmap
*/

import { useEffect, useReducer, useRef, useState } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import './App.css';

function App() {
  const [isDrawing, setIsDrawing] = useState(false);
  const [shapeType, setShapeType] = useState("polygon");
  const [geometries, setGeometries] = useState([]);
  const [selectedGeometry, setSelectedGeometry] = useState(null);
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const [showSettings, setShowSettings] = useState(false);
  const [showOverlays, setShowOverlays] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Handler for ToolUI 'Toggle ZOne
  const handleToggleDrawing = () => {
    console.log("Toggled Zoning:", !isDrawing);
    setIsDrawing((prev) => {
      const newState = !prev;

      // notification of tool state
      toast.info(`Zoning Tool ${newState ? "Enabled" : "Disabled"}`, {
        position: "bottom-right",
        autoClose: 2000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: false,
        draggable: false,
      });
      return newState
    });
  };

  const handleToggleOverlays = () => {
    setShowOverlays((prev) => !prev);
    console.log("Overlays toggled:", !showOverlays);
  };

  const handleToggleFilters = () => {
    setShowFilters((prev) => !prev);
    console.log("Filters toggled: ", !showFilters);
  };

  // Undos previous point placed, will undo until the stack is empty
  const handleUndo = () => {
    setGeometries((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      updated[updated.length - 1].positions.pop();
      return updated;
    });
  };

  // Clears entire cesium viewer of geometries
  const handleClear = () => {
    setGeometries([]);
    setSelectedGeometry(null);
    setShowContextMenu(false);
  };

  // Radio buttons selected in ToolsUI
  const handleSelectShape = (shape) => {
    setShapeType(shape);
  };

  /*
    Should rename the selected geometry. Currently non-functional.
    Implementation may depend on information stored in the database.
    Note: Cesium Entities have a __name attribute. 
  */
  const handleRename = (newName) => {
    setGeometries((prev) =>
      prev.map((geo) =>
        geo === selectedGeometry ? { ...geo, name: newName } : geo
      )
    );
    setSelectedGeometry((prev) => ({ ...prev, name: newName }));
  };

  /* 
    Should delete a selected geometry, but is currently non-functional.
    Implementation may depend on information stored in the database.
    Note: Cesium Entities have a __id attribute. 
  */
  const handleDelete = () => {
    setGeometries((prev) => prev.filter((geo) => geo !== selectedGeometry));
    setShowSettings(false);
    setSelectedGeometry(null);
    setShowContextMenu(false);
  };

  // Placeholder for save functionality
  const handleSave = () => {
    console.log("Zone settings saved.");
    setShowSettings(false);
  };

  // Debug
  console.log("Show Context Menu:", showContextMenu);
  console.log("Selected Geometry:", selectedGeometry);
  console.log("Context Menu Position:", contextMenuPosition);
  console.log("showSettings:", showSettings);

  return (
    <div>
      <ToastContainer />
      <ToolsUI
        onToggleDrawing={handleToggleDrawing}
        onUndo={handleUndo}
        onClear={handleClear}
        onSelectShape={handleSelectShape}
        onToggleOverlays={handleToggleOverlays}
        onToggleFilters={handleToggleFilters}
      />
      <CustomGeometry
        isDrawing={isDrawing}
        shapeType={shapeType}
        geometries={geometries}
        setGeometries={setGeometries}
        setSelectedGeometry={setSelectedGeometry}
        setShowContextMenu={setShowContextMenu}
        setContextMenuPosition={setContextMenuPosition}
        setShowSettings={setShowSettings}
      />

      {showContextMenu && selectedGeometry && (

        <div
          className="context-menu"
          style={{

            top: contextMenuPosition.y,
            left: contextMenuPosition.x,

          }}
        >
          <button onClick={() => setShowSettings(true)}>Settings</button>
          <button onClick={handleDelete}>Delete</button>
          <button onClick={() => setShowSettings(true)}>
            Rename
          </button>
        </div>
      )}

      {showSettings && selectedGeometry && (

        <ZoneSettingsUI
          zoneName={selectedGeometry.name || "Untitled Zone"}
          onRename={handleRename}
          onDelete={handleDelete}
          onSave={handleSave}
        />

      )}
    </div>
  );
}

export default App;