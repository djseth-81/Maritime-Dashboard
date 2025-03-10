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

function App() {
  const [vessels, setVessels] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
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
  }, []);

  const handleFilterApply = async (filters) => {
    await fetchVessels(filters);
  };

  const handleToggleFilters = () => {
    setShowFilters((prev) => !prev);
  };

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

      </Viewer>

      <ToolsUI
        onToggleFilters={handleToggleFilters}
        apiEndpoint="http://localhost:5000/filters/"
        onFilterApply={handleFilterApply}
      />

      {showFilters && (
        <FiltersUI 
          apiEndpoint="http://localhost:5000/filters/" 
          onFilterApply={handleFilterApply}
        />
      )}
    </div>
  );
}

export default App;
