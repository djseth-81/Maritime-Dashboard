import { useState } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import UIControls from "./utilities/UIControls";
import ZoneSettings from "./utilities/ZoneSettings";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import './App.css';

function App() {
  const [isDrawing, setIsDrawing] = useState(false);
  const [shapeType, setShapeType] = useState("polygon");
  const [geometries, setGeometries] = useState([]);
  const [selectedGeometry, setSelectedGeometry] = useState(null);
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({x: 0, y: 0});
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
        geo === selectedGeometry ? {...geo, name: newName} : geo
      )
    );
    setSelectedGeometry((prev) => ({...prev, name: newName }));
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
  }
  console.log("Show Context Menu:", showContextMenu);
  console.log("Selected Geometry:", selectedGeometry);
  console.log("Context Menu Position:", contextMenuPosition);
  console.log("showSettings:", showSettings);
  return (
    <div>
      <ToastContainer />
      <UIControls
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
      />
      
      {showContextMenu && selectedGeometry && (

        <div 
          className="context-menu"
          style={{
            position: "absolute",
            top: contextMenuPosition.y,
            left: contextMenuPosition.x,
            background: "black",
            padding: "5px",
            border: "1px solid black",
            zIndex: 1000,            
          }}
        >
          
          <button onClick={() => setShowSettings(true)}>Settings</button>
          <button onClick={handleDelete}>Delete</button>
          <button onClick={() => setShowSettings(true)}>
            Rename
          </button>
          

        </div>
      )}
      
      {showSettings && (
        <ZoneSettings
          zoneName={selectedGeometry.name || "Untitled Zone" }
          onRename={handleRename}
          onDelete={handleDelete}
          onSave={handleSave}
      />        
      )}
    </div>
  );
}

export default App;