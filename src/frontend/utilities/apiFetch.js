import axios from "axios";
import { toast } from "react-toastify";

/**
 * Fetches vessels from the API and sets the state.
 * @param {string} vesselsAPI - The API endpoint for fetching vessels.
 * @param {Object} filters - The filters to apply when fetching vessels.
 * @param {Function} setVessels - The state setter function for vessels.
 * @returns {Promise<void>}
 * @description This function constructs the query parameters based on the provided filters,
 */

export const fetchVessels = async (vesselsAPI, filters = {}, setVessels) => {
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

  try {
    const response = await axios.get(vesselsAPI, { params: queryParams });

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

export const zoning = async (filters = {}) => {
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