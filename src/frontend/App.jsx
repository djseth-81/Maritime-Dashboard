import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
import ConfirmationDialog from "./utilities/ConfirmationDialog";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import "./App.css";
import { Viewer } from "resium";
import { fetchVessels } from "./utilities/apiFetch";
import { zoning } from "./utilities/zoning/zoning";
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
import { toggleEEZVisibility } from "./utilities/zoning/eezFetch"; // EEZ Functions
import { Cartesian3, Color, HeightReference } from "cesium";
import * as Cesium from "cesium";
import { Entity } from "resium";
import { ImageryLayer } from "resium";
import VesselTracking from "./utilities/shippingVessels/VesselTracking";

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
    types: [],
    statuses: [],
    origin: ""
  })
  const [showEEZ, setShowEEZ] = useState(false);
  const [entityName, setEntityName] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [activeWeatherLayer, setActiveWeatherLayer] = useState(null);
  const [weatherLayers, setWeatherLayers] = useState(null);

  const viewerRef = useRef(null);
  const customGeomRef = useRef(null);
  const URL = window.location.href.split(":");
  const vesselsAPI = "http:" + URL[1] + ":8000/vessels/";
  const filtersAPI = "http:" + URL[1] + ":8000/filters/";
  const eezAPI = "http:" + URL[1] + ":8000/eezs/";
  const wsAPI = "http:" + URL[1] + ":8000/ws";
  const openWeatherAPIKEY = "";

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
      if (selectedGeometry) {
        await zoning(polygonData, filters, setVessels);
      } else {
        console.log("NO ZONE SELECTED");
        await fetchVessels(vesselsAPI, filters, setVessels);
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

    try {
      // Get the polygon data for the selected geometry
      const polygonData = geometries.find(geo => geo.id === selectedGeometry.id);
      if (!polygonData) {
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
            return {
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
    } catch (error) {
      console.error("Error refreshing zone data: ", error);
      toast.error("Failed to refresh zone data.");
    }
  };

  // Handler for toggling EEZ
  const handleToggleEEZ = async () => {
    console.log("EEZ toggle button clicked. Current state:", showEEZ);
    if (!viewerRef.current?.cesiumElement) return;

    const viewer = viewerRef.current.cesiumElement;
    try {
      await toggleEEZVisibility(viewer, showEEZ, setShowEEZ, eezAPI);
    } catch (error) {
      console.error("Error toggling EEZ visibility:", error);
      toast.error("Failed to toggle EEZ visibility.");
    }
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
      }
    };
    loadWeatherLayers(); // Load weather layers
    loadVessels().then(() => {
      const ws = new WebSocket(wsAPI);

      ws.onopen = () => {
        console.log("WebSocket connected from React");
        ws.send("Hello from React WebSocket client!");
      };

      ws.onmessage = (event) => {
        console.log("Message from WebSocket server:", event.data);
        try {
          const message = JSON.parse(event.data);

          if (message.topic === "Vessels") {
          setVessels((prevVessels) =>
            prevVessels.map((vessel) =>
              vessel.mmsi === message.mmsi &&
              (vessel.lat !== message.lat || vessel.lon !== message.lon)
                ? { ...vessel, ...message }
                : vessel
            )
          );
        }

          if (message.topic === "Weather") {
            // Handle weather-related messages here
          }

          if (message.topic === "Ocean") {
            // Handle ocean-related messages here
          }

          if (message.topic === "Events") {
            // Handle event-related messages here
          }

          if (message.topic === "Users") {
            // Handle user-related messages here
          }

        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
      };

      ws.onclose = () => {
        console.log("WebSocket disconnected");
      };

      return () => ws.close();
    });
  }, [viewerReady, vesselsAPI]);

  /*
   * Path prediction
   */
  const performPrediction = async () => {

    function convertToRadians(degrees) {
      return degrees * (Math.PI / 180);
    }

    function convertToDegrees(radians) {
      return radians * (180 / Math.PI);
    }

    function getDistanceInMeters(sog) {
      const nauticalMileInMeters = 1852;
      return sog * nauticalMileInMeters;
    }

    function adjustCoordinates(lat, lon, sog, heading) {
      const R = 6371000;

      const distance = getDistanceInMeters(sog);

      const headingRad = convertToRadians(heading);

      const deltaLat = (distance * Math.cos(headingRad)) / R;
      const deltaLon = (distance * Math.sin(headingRad)) / (R * Math.cos(Math.PI * lat / 180));

      const newLat = lat + convertToDegrees(deltaLat);
      const newLon = lon + convertToDegrees(deltaLon);

      return { newLat, newLon };
    }

    function predictCoordinates(lat, lon, sog, heading) {
      let predictions = [];

      for (let hour = 1; hour <= 24; hour++) {
        const { newLat, newLon } = adjustCoordinates(lat, lon, sog, heading);

        predictions.push({
          "Hours Ahead": hour,
          "Predicted LAT": newLat,
          "Predicted LON": newLon
        });

        lat = newLat;
        lon = newLon;
      }

      return predictions;
    }

    const vesselData = vessels.find(
      (vessel) => vessel.vessel_name === selectedGeometry?.name.split(": ")[1]
    );

    if (vesselData == null) {
      toast.info("No vessel data available");
      return;
    }

    var lat = String(vesselData.lat);
    var lon = String(vesselData.lon);
    var sog = String(vesselData.speed);
    // var cog = String(vesselData.cog);
    var heading = String(vesselData.heading);
    // if backend hosted on a different server than replace url with correct one
    // var url = "http://127.0.0.1:8000/predict/" + lat + "/" + lon + "/" + sog + "/" + heading;
    // const res = await axios.get(url);
    // console.log("Selected Ship data: ", res.data);  
    const predictedCoordinates = predictCoordinates(Number(lat), Number(lon), Number(sog), Number(heading));
    setPredictions(predictedCoordinates);
  }

  function plotPredictedPath(data) {
    const { 'Predicted LAT': latitude, 'Predicted LON': longitude, 'Hours Ahead': hoursAhead } = data;

    const numLongitude = Number(longitude);
    const numLatitude = Number(latitude);

    if (isNaN(numLongitude) || isNaN(numLatitude)) {
      console.warn(`Invalid coordinates for prediction at T+${hoursAhead}h`, { latitude, longitude });
      return null;
    }

    const position = Cartesian3.fromDegrees(numLongitude, numLatitude);

    return (
      <Entity
        key={`dot-${hoursAhead}-${longitude}-${latitude}`}
        position={position}
        point={{
          pixelSize: 10,
          color: Color.AQUA,
          outlineWidth: 2,
          heightReference: HeightReference.CLAMP_TO_GROUND,
        }}
        label={{
          text: `${hoursAhead}h`,
          font: "10pt sans-serif",
          fillColor: Color.LIGHTBLUE,
          outlineColor: Color.BLACK,
          outlineWidth: 2,
          pixelOffset: new Cartesian3(0, -20, 15),
        }}
      />
    );
  }

  /*
   * Weather overlays
   */
  function loadWeatherLayers() {
    if (openWeatherAPIKEY == "" || openWeatherAPIKEY == null) {
      return
    }
    // IOWA WEATHER MAP (ONLY U.S. BASED)
    let currentTime = new Date();
    const radarLayer = new Cesium.WebMapServiceImageryProvider({
      url: "https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi?",
      layers: "nexrad-n0r",
      credit: "Radar data courtesy Iowa Environmental Mesonet",
      parameters: {
        transparent: "true",
        format: "image/png",
        TIME: currentTime.toISOString(),
      },
    });

    // cloud layer from OpenWeatherMap
    const cloudLayer = new Cesium.UrlTemplateImageryProvider({
      url: `https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${openWeatherAPIKEY}`,
      credit: "Cloud layer © OpenWeatherMap",
    });

    // precipitation layer from OpenWeatherMap
    const precipitationLayer = new Cesium.UrlTemplateImageryProvider({
      url: `https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${openWeatherAPIKEY}`,
      credit: "Cloud layer © OpenWeatherMap",
    });

    // wind layer from OpenWeatherMap
    const windLayer = new Cesium.UrlTemplateImageryProvider({
      url: `https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=${openWeatherAPIKEY}`,
      credit: "Cloud layer © OpenWeatherMap",
    });

    // temperature layer from OpenWeatherMap
    const temperatureLayer = new Cesium.UrlTemplateImageryProvider({
      url: `https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${openWeatherAPIKEY}`,
      credit: "Cloud layer © OpenWeatherMap",
    });

    const layerOptions = {
      Clouds: cloudLayer,
      Precipitation: precipitationLayer,
      Wind: windLayer,
      Temperature: temperatureLayer,
      "US Precipitation": radarLayer
    };

    setWeatherLayers(layerOptions)
  }

  const handleClearPredictions = () => {
    setPredictions([]);
  };
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
  //     convertCartesianconvertToDegrees(point)
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
        {/* {vessels.map((vessel) =>
          placeVessel(
            vessel["mmsi"],
            vessel["lon"],
            vessel["lat"],
            vessel["heading"],
            0,
            vessel["type"],
            vessel["vessel_name"]
          ) || <div key={vessel["mmsi"]}>Invalid Vessel Data</div>
        )} */}

        <VesselTracking
          vessels={vessels}
        />

        {predictions && predictions.map((item, index) => plotPredictedPath(item))}

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
          setEntityName={setEntityName}
        />
        {activeWeatherLayer && (
          <ImageryLayer imageryProvider={weatherLayers[activeWeatherLayer]} />
        )}
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
        activeWeatherLayer={activeWeatherLayer}
        onActiveWeatherLayer={setActiveWeatherLayer}
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
          <button onClick={() => performPrediction()}>Predict Possible Path</button>
          {predictions.length > 0 && <button onClick={handleClearPredictions}>Clear Predicted Path</button>}
          {polygonData && (<button onClick={() => { handleRefreshZoneData(); setShowContextMenu(false); }}>Refresh Zone</button>)}
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
