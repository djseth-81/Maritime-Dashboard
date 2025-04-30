import { toast } from "react-toastify";
import { GeoJsonDataSource, Color } from "cesium";
import axios from "axios";

/**
 * @description Fetches EEZ zones from the API.
 * @param {string} eezAPI - The API endpoint for fetching EEZ zones.
 * @returns {Promise<Array>} - The array of EEZ zones.
 */
export const fetchEEZZones = async (eezAPI) => {
  try {
    console.log("Fetching EEZ zones from API:", eezAPI);
    const response = await axios.get(eezAPI);
    console.log("EEZ API response:", response.data);
    if (!response.data?.payload?.length) {
      toast.info("No EEZ zones found.");
      return [];
    }
    return response.data.payload;
  } catch (error) {
    console.error("Error fetching EEZ zones:", error.message);
    toast.error("Failed to load EEZ zones.");
    return [];
  }
};

/**
 * @description Loads EEZ zones to the globe using Cesium's GeoJsonDataSource.
 * @param {Object} viewer - The Cesium viewer instance.
 * @param {Array} zones - The array of EEZ zones to load.
 * @returns {Promise<GeoJsonDataSource|null>} - The loaded GeoJsonDataSource or null if an error occurs.
 */
export const loadEEZZonesToGlobe = async (viewer, zones) => {
  if (!viewer || !zones?.length) return null;

  try {
    const dataSource = new GeoJsonDataSource("EEZ Zones");
    const brightPurple = Color.PURPLE;
    const brightPurpleTransparent = Color.PURPLE.withAlpha(0.4);

    for (const zone of zones) {
      const geometry = typeof zone.geom === "string" ? JSON.parse(zone.geom) : zone.geom;
      const feature = {
        type: "Feature",
        properties: { id: zone.id, name: zone.name || `EEZ Zone ${zone.id}`, type: "EEZ" },
        geometry,
      };

      const featureDataSource = await GeoJsonDataSource.load(feature, {
        stroke: brightPurple,
        fill: brightPurpleTransparent,
        strokeWidth: 3,
      });

      featureDataSource.entities.values.forEach((entity) => {
        entity.polygon.material = brightPurpleTransparent;
        entity.polygon.outlineColor = brightPurple;
        entity.polygon.outlineWidth = 3;
        dataSource.entities.add(entity);
      });
    }

    viewer.dataSources.add(dataSource);
    return dataSource;
  } catch (error) {
    console.error("Error loading EEZ zones to globe:", error);
    toast.error("Failed to display EEZ zones on the globe.");
    return null;
  }
};

export const toggleEEZVisibility = async (viewer, currentVisibility, setVisibility, eezAPI) => {
  if (!viewer) return;

  console.log("Current EEZ visibility:", currentVisibility);

  const eezDataSources = viewer.dataSources.getByName("EEZ Zones");

  if (eezDataSources?.length > 0) {
    console.log("Toggling visibility of existing EEZ data source...");
    eezDataSources[0].show = !currentVisibility;
    setVisibility(!currentVisibility);
    toast.info(`EEZ zones ${!currentVisibility ? "shown" : "hidden"}`);
  } else if (!currentVisibility) {
    console.log("Fetching and loading EEZ zones...");
    try {
      const zones = await fetchEEZZones(eezAPI);
      console.log("Fetched EEZ zones:", zones);
      await loadEEZZonesToGlobe(viewer, zones);
      setVisibility(true);
      toast.success("EEZ zones loaded successfully!");
    } catch (error) {
      console.error("Error loading EEZ zones:", error);
      toast.error("Failed to load EEZ zones.");
      setVisibility(false);
    }
  }
};
