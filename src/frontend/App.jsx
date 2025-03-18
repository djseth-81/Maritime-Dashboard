import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
import FiltersUI from "./utilities/filters/FiltersUI";
import ConfirmationDialog from "./utilities/ConfirmationDialog";
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
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const viewerRef = useRef(null);
  const URL = window.location.href.split(':');
  const vesselsAPI = "http:" + URL[1] + ":8000/vessels/";
  const filtersAPI = "http:" + URL[1] + ":8000/filters/";

  // Fetch vessels from API
  const fetchVessels = async (filters = {}) => {
    try {
      const queryParams = {};

      if (filters.types && filters.types.length > 0) {
        queryParams.type = filters.types.join(",");
      }

      if (filters.origin) {
        queryParams.origin = filters.origin;
      }

      if (filters.statuses && filters.statuses.length > 0) {
        queryParams.status = filters.statuses.join(",");
      }

      const response = await axios.get(vesselsAPI, { params: queryParams });
      
      console.log("Table privileges");
      console.log(response.data.Privileges);

      console.log("Response Timestamp");
      console.log(response.data.retrieved);

      console.log("Size of payload");
      console.log(response.data.size);

      if (response.data.length === 0) {
        toast.info("No vessels found matching your filters.");
        setVessels([]);
        return;
      }

      const transformedVessels = response.data.payload.map((vessel) =>
        Array.isArray(vessel)
          ? {
            id: vessel['mmsi'],
            name: vessel['vessel_name'],
            type: vessel['type'],
            country_of_origin: vessel['flag'],
            status: vessel['current_status'],
            latitude: vessel['lat'],
            longitude: vessel['lon']
          }
          : vessel
      );

      setVessels(transformedVessels);

    } catch (error) {
      console.error("Error fetching vessels:", error.message);
      toast.error("Failed to load vessels.");
      setVessels([]);
    }
  };

  useEffect(() => {
    fetchVessels();
    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);
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

  const handleToggleFilters = () => setShowFilters((prev) => !prev);

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
    setShowClearDialog(true);
  };

  const handleClearConfirmed = () => {
    setGeometries([]);
    setSelectedGeometry(null);
    setShowContextMenu(false);
    setShowClearDialog(false);
  };

  const handleClearCancelled = () => {
    setShowClearDialog(false);
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
        geo.id === selectedGeometry ? { ...geo, name: newName } : geo
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
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedGeometry) {
      // Remove the selected geometry from the Cesium viewer
      viewerRef.current.cesiumElement.entities.removeById(selectedGeometry);

      // Update the state to remove the selected geometry
      setGeometries((prev) => prev.filter((geo) => geo.id !== selectedGeometry));
    }
    setShowDeleteDialog(false);
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  // Placeholder for save functionality
  const handleSave = () => {
    console.log("Zone settings saved.");
    setShowSettings(false);
  };

  const handleFilterApply = async (filters) => {
        console.log("Filters selected:");
        console.log(filters);
        await fetchVessels(filters);
    }

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
            vessel['lon'],
            vessel['lat'],
            0, //For elevation
            vessel['type'],
            vessel['name']
          ) || <div key={vessel['mmsi']}>Invalid Vessel Data</div>
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
        onToggleFilters={handleToggleFilters}
        apiEndpoint={filtersAPI}
        onFilterApply={handleFilterApply}
        onToggleDrawing={handleToggleDrawing}
        onUndo={handleUndo}
        onClear={handleClear}
        onSelectShape={handleSelectShape}
        onToggleOverlays={handleToggleOverlays}
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
          apiEndpoint={filtersAPI}
          onFilterApply={handleFilterApply}
        />
      )}

      {showOverlays && (
        <OverlaysUI
          onClose={() => setShowOverlays(false)}
          onToggleWeather={() => console.log("Weather Overlay Toggled")}
        />
      )}

      {showClearDialog && (
        <ConfirmationDialog
          message="Are you sure you want to clear all geometries?"
          onConfirm={handleClearConfirmed}
          onCancel={handleClearCancelled}
        />
      )}

      {showDeleteDialog && (
        <ConfirmationDialog
          message="Are you sure you want to delete the selected geometry?"
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
        />
      )}
    </div>
  );
}

export default App;
