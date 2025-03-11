import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
import FiltersUI from "./utilities/filters/FiltersUI";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import './App.css';
import { placeVessel } from "./utilities/shippingVessels/Vessels";
import { Viewer } from "resium";
import { SceneMode } from "cesium";
import axios from "axios";
import OverlaysUI from "./utilities/OverlaysUI";

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
  const [vessels, setVessels] = useState([]);
  const [viewerReady, setViewerReady] = useState(false);

  const viewerRef = useRef(null);
  const apiEndpoint = "http://localhost:5000/vessels/";

  // Fetch vessels from API
  const fetchVessels = async (filters = {}) => {
    try {
      const response = await axios.get(apiEndpoint, { params: filters });

      if (response.data.length === 0) {
        toast.info("No vessels found matching your filters.", {
          position: "bottom-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: false,
          draggable: false,
        });
        setVessels([]);  // Clear vessels
        return;
      }

      console.log("Fetched Vessels (Raw Data):", response.data);

      const transformedVessels = response.data.map((vessel) =>
        Array.isArray(vessel)
          ? {
            id: vessel[0],
            name: vessel[1],
            type: vessel[2],
            country_of_origin: vessel[3],
            status: vessel[4],
            latitude: vessel[5],
            longitude: vessel[6]
          }
          : vessel
      );

      console.log("Transformed Vessels:", transformedVessels);
      setVessels(transformedVessels);

    } catch (error) {
      if (error.response?.status === 500) {
        toast.error("Server error occurred. Please try again later.", {
          position: "bottom-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: false,
          draggable: false,
        });
      } else {
        toast.info("No vessels found matching your filters.", {
          position: "bottom-right",
          autoClose: 3000,
          hideProgressBar: true,
          closeOnClick: true,
          pauseOnHover: false,
          draggable: false,
        });
      }

      console.error("Error fetching vessels:", error.message);
      setVessels([]);  // Clear vessels
    }
  };

  useEffect(() => {
    fetchVessels();  // Fetch all vessels

    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);  // Set viewerReady to true
      // Create a scene mode change event handler
      const sceneModeChangeHandler = () => {
        if (viewer.selectedEntity) {
          const currentEntity = viewer.selectedEntity;
          viewer.selectedEntity = undefined;
          setTimeout(() => {
            viewer.selectedEntity = currentEntity;
          }, 100);
        }
      };

      viewer.scene.morphComplete.addEventListener(sceneModeChangeHandler);

      return () => {
        if (viewer && viewer.scene && !viewer.isDestroyed()) {
          viewer.scene.morphComplete.removeEventListener(sceneModeChangeHandler);
        }
      };
    }
  }, [viewerRef.current]);

  // Handler for ToolUI 'Toggle Zoning'
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
      return newState;
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
  
  const handleFilterApply = async (filters) => {
    await fetchVessels(filters);
  };

  // Debug
  console.log("Show Context Menu:", showContextMenu);
  console.log("Selected Geometry:", selectedGeometry);
  console.log("Context Menu Position:", contextMenuPosition);
  console.log("showSettings:", showSettings);
  
  return (
    <div className="cesium-viewer">
      <ToastContainer />
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
        infoBox={true}
        selectionIndicator={true}>

        {vessels.map((vessel) =>
          placeVessel(
            vessel.longitude,
            vessel.latitude,
            0, //For elevation
            vessel.type,
            vessel.name
          ) || <div key={vessel.id}>Invalid Vessel Data</div>
        )}

        <CustomGeometry
          viewer={viewerRef}
          viewerReady={viewerReady}
          isDrawing={isDrawing}
          shapeType={shapeType}
          geometries={geometries}
          setGeometries={setGeometries}
          setSelectedGeometry={setSelectedGeometry}
          setShowContextMenu={setShowContextMenu}
          setContextMenuPosition={setContextMenuPosition}
          setShowSettings={setShowSettings}
        />
      </Viewer>

      <ToolsUI
        onToggleDrawing={handleToggleDrawing}
        onUndo={handleUndo}
        onClear={handleClear}
        onSelectShape={handleSelectShape}
        onToggleOverlays={handleToggleOverlays}
        onToggleFilters={handleToggleFilters}
        onFilterApply={handleFilterApply}
      />

      {showContextMenu && selectedGeometry && (
        <div
          className="context-menu"
          style={{ top: contextMenuPosition.y, left: contextMenuPosition.x }}
        >
          <button onClick={() => setShowSettings(true)}>Settings</button>
          <button onClick={handleDelete}>Delete</button>
          <button onClick={() => setShowSettings(true)}>Rename</button>
        </div>
      )}

      {showSettings && selectedGeometry && (
        <ZoneSettingsUI
          selectedGeometry={selectedGeometry}
          onRename={handleRename}
          onDelete={handleDelete}
          onSave={handleSave}
        />
      )}

      {showFilters && (
        <FiltersUI
          apiEndpoint="http://localhost:5000/filters/"
          onFilterApply={handleFilterApply}
        />
      )}

      {showOverlays && (
        <OverlaysUI
          onClose={() => setShowOverlays(false)}
          onToggleWeather={() => console.log("Weather Overlay Toggled")}
        />
      )}
    </div>
  );
}

export default App;
