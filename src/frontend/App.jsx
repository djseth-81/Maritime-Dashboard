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

  const handleToggleDrawing = () => {
    console.log("Toggled Zoning:", !isDrawing);
    setIsDrawing((prev) => {
      const newState = !prev;
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

  const handleUndo = () => {
    setGeometries((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      updated[updated.length - 1].positions.pop();
      return updated;
    });
  };

  const handleClear = () => {
    setGeometries([]);
    setSelectedGeometry(null);
    setShowContextMenu(false);
  };

  const handleSelectShape = (shape) => {
    setShapeType(shape);
  };

  const handleRename = (newName) => {
    setGeometries((prev) =>
      prev.map((geo) =>
        geo === selectedGeometry ? { ...geo, name: newName } : geo
      )
    );
    setSelectedGeometry((prev) => ({ ...prev, name: newName }));
  };

  const handleDelete = () => {
    setGeometries((prev) => prev.filter((geo) => geo !== selectedGeometry));
    setShowSettings(false);
    setSelectedGeometry(null);
    setShowContextMenu(false);
  };

  const handleSave = () => {
    console.log("Zone settings saved.");
    setShowSettings(false);
  };

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
          // ref={contextMenuRef}
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
        // <div ref={settingsRef}>
        <ZoneSettingsUI
          zoneName={selectedGeometry.name || "Untitled Zone"}
          onRename={handleRename}
          onDelete={handleDelete}
          onSave={handleSave}
        />
        // </div>       
      )}
    </div>
  );
}

export default App;