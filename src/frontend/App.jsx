import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
// import FiltersUI from "./utilities/filters/FiltersUI";
import ConfirmationDialog from "./utilities/ConfirmationDialog";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import "./App.css";
import { placeVessel } from "./utilities/shippingVessels/Vessels";
import { Viewer } from "resium";
// import { SceneMode, Cartographic, Math } from "cesium";
// import axios from "axios";
import OverlaysUI from "./utilities/overlays/OverlaysUI";
import { fetchVessels } from "./utilities/apiFetch";
import { zoning } from "./utilities/zoning";
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
  const customGeomRef = useRef(null);
  const URL = window.location.href.split(":");
  const vesselsAPI = "http:" + URL[1] + ":8000/vessels/";
  const filtersAPI = "http:" + URL[1] + ":8000/filters/";
  
  useCesiumViewer(viewerRef, setViewerReady);
  
  const handleFilterApply = async (filters) => {
    console.log("Applying filters...", filters);
    try {
      await fetchVessels(vesselsAPI, filters, setVessels);
      if (selectedGeometry) {
        await zoning(polygonData, filters, setVessels);
      } else {
        console.log("NO ZONE SELECTED");
      }
    } catch (error) {
      console.error("Error applying filters:", error.message);
      toast.error("Failed to apply filters.");
    }
  };
  const polygonData = geometries?.find(
    (geo) => geo.id === selectedGeometry?.id
  );

  // Default filters for vessels
  const defaultFilters = {
    types: ["CARGO", "FISHING", "TANKER", "TUG", "PASSENGER",
      "RECREATIONAL", "OTHER"],
    statuses: [
      "UNDERWAY", "ANCHORED", "MOORED", "IN TOW", "FISHING",
      "UNMANNED", "LIMITED MOVEMENT", "HAZARDOUS CARGO",
      "AGROUND", "EMERGENCY", "UNKNOWN",
    ],
  }

  // useEffect(() => { Redudant code for scene mode change event handler
  //   if (viewerRef.current && viewerRef.current.cesiumElement) {
  //     const viewer = viewerRef.current.cesiumElement;
  //     setViewerReady(true);
  //     // Create a scene mode change event handler
  //     const sceneModeChangeHandler = () => {
  //       // If there's a selected entity, re-select it to update the info box position
  //       if (viewer.selectedEntity) {
  //         const currentEntity = viewer.selectedEntity;
  //         viewer.selectedEntity = undefined; // Deselect
  //         setTimeout(() => {
  //           viewer.selectedEntity = currentEntity; // Re-select after a brief delay
  //         }, 100);
  //       }
  //     };

  //     // Add event listener for scene mode changes
  //     viewer.scene.morphComplete.addEventListener(sceneModeChangeHandler);

  //     // Clean up event listener when component unmounts
  //     return () => {
  //       if (viewer && viewer.scene && !viewer.isDestroyed()) {
  //         viewer.scene.morphComplete.removeEventListener(
  //           sceneModeChangeHandler
  //         );
  //       }
  //     };
  //   }
  // }, [viewerRef.current]);


  // Fetch vessels when the viewer is ready and the API endpoint is available
  useEffect(() => {
    const loadVessels = async () => {
      try {
        console.log("Fetching vessels...");
        await fetchVessels(vesselsAPI, defaultFilters, setVessels);
      } catch (error) {
        console.error("Error fetching vessels:", error.message);
        toast.error("Failed to load vessels.");
      };
    };
    loadVessels();
  }, [viewerReady, vesselsAPI]);

  // Debug
  // console.log("Show Context Menu:", showContextMenu);
  // console.log("Context Menu Position:", contextMenuPosition);
  // console.log("showSettings:", showSettings);

  // console.log("Selected Geometry:", selectedGeometry);
  // console.log("selectedGeometry Name: ", selectedGeometry?.name);
  // console.log("Selected Geometry ID:", selectedGeometry?.id);
  // console.log("Selected Geometry Positions:");
  // console.log(
  //   geometries.find((geo) => geo.id === selectedGeometry?.id)?.positions.map((point) =>
  //     convertCartesianToDegrees(point)
  //   )
  // );

  // SHIP DATA
  // console.log("SHIP DATA:");
  // console.log(vessels);
  // console.log("SHIP NAME:");
  // if (selectedGeometry?.name) {
  //   console.log(selectedGeometry.name.split(": ")[1]);
  // } else {
  //   console.log("No ship selected.");
  // }
  // const vesselData = vessels.find(
  //   (vessel) => vessel.vessel_name === selectedGeometry?.name.split(": ")[1]
  // );
  // console.log("Selected Ship data: ", vesselData);
  // console.log("Selected ship position:");
  // console.log(vesselData?.geom);
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
        infoBoxViewModel={{sanitizeHtml: false,
        }}
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
          ref={customGeomRef}
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
        onUndo={() => {console.log("Undo function passed to handleUndo:", customGeomRef.current?.undoLastPoint);
          handleUndo(customGeomRef.current?.undoLastPoint)}}
        onClear={() => handleClear(setShowClearDialog)}
        onToggleOverlays={() => handleToggleOverlays(showOverlays, setShowOverlays)}
      />

      {showContextMenu && selectedGeometry && (
        <div
          className="context-menu"
          style={{ top: contextMenuPosition.y, left: contextMenuPosition.x }}
        >
          <button onClick={() => { setShowSettings(true); setShowContextMenu(false); }}>Settings</button>
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

      {/* {showFilters && (
        <FiltersUI apiEndpoint={filtersAPI} onFilterApply={handleFilterApply} />
      )} */}

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