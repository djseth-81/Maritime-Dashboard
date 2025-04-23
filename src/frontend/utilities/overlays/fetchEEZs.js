import axios from "axios";

export const fetchEEzs = async (eezAPI) => {
  try {
    const response = await axios.get(eezAPI);
    console.log("EEZs response:", response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching EEZs:", error.message);
    throw new Error("Failed to load EEZs.");
  }
}