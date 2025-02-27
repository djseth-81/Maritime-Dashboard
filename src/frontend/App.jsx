import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import UIControls from "./utilities/UIControls";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import './App.css';
import {placeVessel} from "./utilities/shippingVessels/Vessels";
import { Viewer } from "resium";
import { SceneMode } from "cesium";

function App() {
  const [isDrawing, setIsDrawing] = useState(false);
  const [shapeType, setShapeType] = useState("polygon");
  const [geometries, setGeometries] = useState([]);
  const viewerRef = useRef(null);

  // Add an effect to handle scene mode changes
  useEffect(() => {
    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      
      // Create a scene mode change event handler
      const sceneModeChangeHandler = () => {
        // If there's a selected entity, re-select it to update the info box position
        if (viewer.selectedEntity) {
          const currentEntity = viewer.selectedEntity;
          viewer.selectedEntity = undefined; // Deselect
          setTimeout(() => {
            viewer.selectedEntity = currentEntity; // Re-select after a brief delay
          }, 100);
        }
      };
      
      // Add event listener for scene mode changes
      viewer.scene.morphComplete.addEventListener(sceneModeChangeHandler);
      
      // Clean up event listener when component unmounts
      return () => {
        if (viewer && viewer.scene && !viewer.isDestroyed()) {
          viewer.scene.morphComplete.removeEventListener(sceneModeChangeHandler);
        }
      };
    }
  }, []);

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
  };

  const handleSelectShape = (shape) => {
    setShapeType(shape);
  };

  return (
    <div className="cesium-container">
      <div>
        {/* UI Controls and Custom Geometry */}
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
        />
    </div>
      <Viewer
      ref={viewerRef}
      full
      timeline={false}
      animation={false}
      homeButton={true}
      baseLayerPicker={true}
      navigationHelpButton={false}
      sceneModePicker={true}
      geocoder={true}
      infoBox={true} // Important for seeing vessel descriptions
      selectionIndicator={true}>

        {/* Place a cargo vessel */}
        {placeVessel(-122.4194, 37.7749, 1000, "cargo", "Cargo Ship 1")}

        {/* Place a fishing vessel */}
        {placeVessel(-74.0060, 40.7128, 0, "fishing", "Fishing Boat 1")}
        
      </Viewer>
    </div>
  );
}

export default App;