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
import { generateZoneDescription } from "./utilities/zoning/ZoneInfobox";
import { fetchEEZZones, loadEEZZonesToGlobe, toggleEEZVisibility } from "./utilities/zoning/eezFetch"; // EEZ Functions

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
  const [currentFilters, setCurrentFilters] = useState({  // Tracks current filters
    types:[],
    statuses: [],
    origin:""
  })
  const [showEEZ, setShowEEZ] = useState(false);
  
  const viewerRef = useRef(null);
  const customGeomRef = useRef(null);
  const URL = window.location.href.split(":");
  const vesselsAPI = "http:" + URL[1] + ":8000/vessels/";
  const filtersAPI = "http:" + URL[1] + ":8000/filters/";
  const eezAPI = "http:" + URL[1] + ":8000/eezs/";

  useCesiumViewer(viewerRef, setViewerReady);

  // const handleFilterApply = async (filters) => {
  //   console.log("Filters selected:");
  //   console.log(filters);
  //   await fetchVessels(vesselsAPI, filters, setVessels);
  //   await selectedGeometry ? zoning(polygonData, filters, setVessels) : console.log("NO ZONE SELECTED");
  // };
  const handleFilterApply = async (filters) => {
    console.log("Applying filters...", filters);

    // Set current filters
    setCurrentFilters(filters);

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

  // Set currentFilters based on defaultFilters once component is mounted
  useEffect(() => {
    setCurrentFilters({
      types: defaultFilters.types,
      statuses: defaultFilters.statuses,
      origin: ""
    });
  }, []);

  const handleRefreshZoneData = async () => {
    if (!selectedGeometry) return;

    try{
      // Get the polygon data for the selected geometry
      const polygonData = geometries.find(geo => geo.id === selectedGeometry.id);
      if (!polygonData){
        toast.error("Selected zone data not found.");
        return;
      }

      // Use the current filters
      const zoneData = await zoning(polygonData, currentFilters);

      if (!zoneData) {
        toast.warning("No data found for this zone.");
        return;
      }

      // Update Geometries state to include the zone data
      setGeometries(prevGeometries =>
        prevGeometries.map(geo => {
          if (geo.id === selectedGeometry.id) {
            return{
              ...geo,
              zoneData: zoneData
            };
          }
          return geo;
        })
      );




      // Update the entity's description with the new data
      if (viewerRef.current && viewerRef.current.cesiumElement) {
        const entity = viewerRef.current.cesiumElement.entities.getById(selectedGeometry.id);
        if (entity) {
          entity.description = generateZoneDescription(selectedGeometry.name, zoneData);
          toast.success("Zone data refreshed successfully!");
        }
      }
    } catch (error){
      console.error("Error refreshing zone data: ", error);
      toast.error("Failed to refresh zone data.");
    }
  };

  // Handler for toggling EEZ
  const handleToggleEEZ = () => {
    if (!viewerRef.current?.cesiumElement) return;

    toggleEEZVisibility(
      viewerRef.current.cesiumElement,
      showEEZ,
      setShowEEZ,
      eezAPI
    );

  };

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

    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("WebSocket connected from React");  //displays message showing websocket is connected (shows on F12 + console)
      ws.send("Hello from React WebSocket client!");  //dispalys on backend log
    };

    ws.onmessage = (event) => {
      console.log("Message from WebSocket server:", event.data);  //echos the response from backend log (shows on F12 + console)
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err); //error handling
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");  //error handling
    };

    return () => ws.close();

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
        infoBoxViewModel={{
          sanitizeHtml: false,
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
        onUndo={() => {
          console.log("Undo function passed to handleUndo:", customGeomRef.current?.undoLastPoint);
          handleUndo(customGeomRef.current?.undoLastPoint)
        }}
        onClear={() => handleClear(setShowClearDialog)}
        onToggleOverlays={() => handleToggleOverlays(showOverlays, setShowOverlays)}
        onToggleEEZ={handleToggleEEZ}
        showEEZState={showEEZ}
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
          onRefreshData={handleRefreshZoneData} //Refreshes data in zone
        />
      )}

      {/* {showFilters && (
        <FiltersUI apiEndpoint={filtersAPI} onFilterApply={handleFilterApply} />
      )} */}

      {/*showOverlays && (
        <OverlaysUI
          onClose={() => handleToggleOverlays(showOverlays, setShowOverlays)}
          onToggleWeather={() => console.log("Weather Overlay Toggled")}
          onToggleEEZ={handleToggleEEZ}
          showEEZState={showEEZ}
        />
      )*/}

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
