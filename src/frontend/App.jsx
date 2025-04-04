import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
import FiltersUI from "./utilities/filters/FiltersUI";
import ConfirmationDialog from "./utilities/ConfirmationDialog";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import "./App.css";
import { placeVessel } from "./utilities/shippingVessels/Vessels";
import { Viewer } from "resium";
import { SceneMode, Cartographic, Math } from "cesium";
import axios from "axios";
import OverlaysUI from "./utilities/overlays/OverlaysUI";
import { convertCartesianToDegrees } from "./utilities/coordUtils";
import { fetchVessels } from "./utilities/apiFetch";
import {
  handleUndo,
  handleToggleDrawing,
  handleToggleOverlays,
  handleToggleFilters,
  handleClear,
  handleClearConfirmed,
  handleClearCancelled,
  handleRename,
  handleDelete,
  handleDeleteConfirm,
  handleDeleteCancel,
  handleSave,
} from "./utilities/eventHandlers";
import { useCesiumViewer } from "./utilities/hooks/useCesiumViewer";
import "./App.css";

function App() {
  const [isDrawing, setIsDrawing] = useState(false);
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
  const URL = window.location.href.split(":");
  const vesselsAPI = "http:" + URL[1] + ":8000/vessels/";
  const filtersAPI = "http:" + URL[1] + ":8000/filters/";

  useCesiumViewer(viewerRef, setViewerReady);

  const handleFilterApply = async (filters) => {
    console.log("Filters selected:", filters);
    await fetchVessels(vesselsAPI, filters, setVessels);
  };

  const zoning = async (filters = {}) => {
    const payload = {};

    // If zone is selected, apply geospatial filtering
    console.log("ZONE SELECTED:");
    const polygonData = geometries.find(
      (geo) => geo.id === selectedGeometry?.id
    );
    let polygonVerticies = polygonData?.positions.map((point) =>
      convertCartesianToDegrees(point) // This is sick tho
    );

    let geom = {
      type: "Polygon",
      coordinates: polygonVerticies?.map((point) => [
        point.longitude,
        point.latitude,
      ]),
    };
    console.log("Zone GeoJSON:");
    console.log(geom);
    payload.geom = geom;
    const zoneAPI = "http:" + URL[1] + ":8000/zoning/";

    // Apply filters to query
    if (filters.types && filters.types.length > 0) {
      payload.type = filters.types.join(",");
    }
    if (filters.origin) {
      payload.origin = filters.origin;
    }
    if (filters.statuses && filters.statuses.length > 0) {
      payload.status = filters.statuses.join(",");
    }

    try {
      const response = await axios.post(zoneAPI, payload);

      console.log("Zoning response:");
      console.log(response);
      console.log("Table privileges");
      console.log(response.data.privileges);
      console.log("Response Timestamp");
      console.log(response.data.retrieved);

      console.log("Size of payload");
      console.log(response.data.size);
      console.log("Payload:");
      console.log(response.data.payload);
      if (response.data.length === 0) {
        toast.info("No vessels found matching your filters.");
        setVessels([]);
        return;
      }

      const transformedVessels = response.data.payload.map((vessel) =>
        Array.isArray(vessel)
          ? {
              id: vessel["mmsi"],
              name: vessel["vessel_name"],
              type: vessel["type"],
              country_of_origin: vessel["flag"],
              status: vessel["current_status"],
              latitude: vessel["lat"],
              longitude: vessel["lon"],
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
    selectedGeometry ? zoning() : console.log("NO ZONE SELECTED"); // Dunno whether or not this actually does anything...

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
          viewer.scene.morphComplete.removeEventListener(
            sceneModeChangeHandler
          );
        }
      };
    }
  }, [viewerRef.current]);

  // Debug
  console.log("Show Context Menu:", showContextMenu);
  console.log("Context Menu Position:", contextMenuPosition);
  console.log("showSettings:", showSettings);

  console.log("Selected Geometry:", selectedGeometry);
  console.log("selectedGeometry Name: ", selectedGeometry?.name);
  // console.log("Selected Geometry ID:", selectedGeometry?.id);
  // console.log("Selected Geometry Positions:");
  // console.log(
  //   geometries.find((geo) => geo.id === selectedGeometry?.id)?.positions.map((point) =>
  //     convertCartesianToDegrees(point)
  //   )
  // );

  // SHIP DATA
  console.log("SHIP DATA:");
  console.log(vessels);
  console.log("SHIP NAME:");
  if (selectedGeometry?.name) {
    console.log(selectedGeometry.name.split(": ")[1]);
  } else {
    console.log("No ship selected.");
  }
  const vesselData = vessels.find(
    (vessel) => vessel.vessel_name === selectedGeometry?.name.split(": ")[1]
  );
  console.log("Selected Ship data: ", vesselData);
  console.log("Selected ship position:");
  console.log(vesselData?.geom);

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
        selectionIndicator={true}
      >
        {vessels.map((vessel) =>
          placeVessel(
            vessel["lon"],
            vessel["lat"],
            vessel["heading"],
            0,
            vessel["type"],
            vessel["vessel_name"]
          ) || <div key={vessel["mmsi"]}>Invalid Vessel Data</div>
        )}

        <CustomGeometry
          viewer={viewerRef}
          viewerReady={viewerReady}
          isDrawing={isDrawing}
          geometries={geometries}
          setGeometries={setGeometries}
          setSelectedGeometry={setSelectedGeometry}
          setShowContextMenu={setShowContextMenu}
          setContextMenuPosition={setContextMenuPosition}
          setShowSettings={setShowSettings}
        />
      </Viewer>

      <ToolsUI
        onToggleFilters={() => handleToggleFilters(setShowFilters)}
        apiEndpoint={filtersAPI}
        onFilterApply={handleFilterApply}
        onToggleDrawing={() => handleToggleDrawing(isDrawing, setIsDrawing)}
        onUndo={() => handleUndo(setGeometries)}
        onClear={() => handleClear(setShowClearDialog)}
        onToggleOverlays={() => handleToggleOverlays(showOverlays, setShowOverlays)}
      />

      {showContextMenu && selectedGeometry && (
        <div
          className="context-menu"
          style={{ top: contextMenuPosition.y, left: contextMenuPosition.x }}
        >
          <button onClick={() => setShowSettings(true)}>Settings</button>
          <button onClick={() => handleDelete(setShowContextMenu, setShowDeleteDialog)}>
            Delete
          </button>
          <button onClick={() => setShowSettings(true)}>Rename</button>
        </div>
      )}

      {showSettings && selectedGeometry && (
        <ZoneSettingsUI
          zoneName={selectedGeometry.name}
          positions={
            geometries.find((geo) => geo.id === selectedGeometry.id)?.positions
          }
          onRename={(newName) =>
            handleRename(newName, selectedGeometry, viewerRef, setGeometries, setSelectedGeometry)
          }
          onDelete={() => handleDelete(setShowContextMenu, setShowDeleteDialog)}
          onSave={() => handleSave(setShowSettings)}
        />
      )}

      {showFilters && (
        <FiltersUI apiEndpoint={filtersAPI} onFilterApply={handleFilterApply} />
      )}

      {showOverlays && (
        <OverlaysUI
          onClose={() => handleToggleOverlays(showOverlays, setShowOverlays)}
          onToggleWeather={() => console.log("Weather Overlay Toggled")}
        />
      )}

      {showClearDialog && (
        <ConfirmationDialog
          message="Are you sure you want to clear all geometries?"
          onConfirm={() =>
            handleClearConfirmed(
              viewerRef,
              setGeometries,
              setSelectedGeometry,
              setShowContextMenu,
              setShowClearDialog
            )
          }
          onCancel={() => handleClearCancelled(setShowClearDialog)}
        />
      )}

      {showDeleteDialog && (
        <ConfirmationDialog
          message="Are you sure you want to delete the selected geometry?"
          onConfirm={() =>
            handleDeleteConfirm(
              selectedGeometry,
              viewerRef,
              setGeometries,
              setSelectedGeometry,
              setShowDeleteDialog
            )
          }
          onCancel={() => handleDeleteCancel(setShowDeleteDialog)}
        />
      )}
    </div>
  );
}

export default App;