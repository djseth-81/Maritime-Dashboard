import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { SceneMode } from 'cesium';

/**
 * Custom hook for vessel tracking and view mode changes
 * @param {Object} viewerRef - Reference to the Cesium viewer
 * @param {string} apiEndpoint - API endpoint for vessel data
 * @returns {Object} - Vessel state and control functions
 */
const useVesselTracking = (viewerRef, apiEndpoint) => {
  const [vessels, setVessels] = useState([]);
  const [viewerReady, setViewerReady] = useState(false);
  const [currentSceneMode, setCurrentSceneMode] = useState(null);
  
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

  // Setup viewer and event listeners
  useEffect(() => {
    fetchVessels();  // Fetch all vessels

    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);
      
      // Initialize current scene mode
      setCurrentSceneMode(viewer.scene.mode);
      
      // Handle scene mode changes (3D, 2D, Columbus)
      const sceneModeChangeHandler = () => {
        // Update the current scene mode
        setCurrentSceneMode(viewer.scene.mode);
        
        // Handle selected entity
        if (viewer.selectedEntity) {
          const currentEntity = viewer.selectedEntity;
          viewer.selectedEntity = undefined;
          setTimeout(() => {
            viewer.selectedEntity = currentEntity;
          }, 100);
        }
        
        // Force vessel redraw when view mode changes
        if (vessels.length > 0) {
          console.log(`View mode changed to ${getSceneModeName(viewer.scene.mode)} - refreshing vessel positions`);
          
          // We need to completely recreate the entities with the correct mode-specific coordinates
          setTimeout(() => {
            // First remove all existing vessel entities (clean slate)
            const entities = viewer.entities.values.filter(entity => 
              entity.name && entity.name.includes('Vessel:')
            );
            
            entities.forEach(entity => {
              viewer.entities.remove(entity);
            });
            
            // Then trigger a fresh render with the vessels data
            setVessels([...vessels]);
          }, 300);
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

  // Helper function to get scene mode name for logging
  const getSceneModeName = (sceneMode) => {
    switch(sceneMode) {
      case SceneMode.SCENE3D: return "3D";
      case SceneMode.SCENE2D: return "2D";
      case SceneMode.COLUMBUS_VIEW: return "Columbus View";
      default: return "Unknown";
    }
  };

  return {
    vessels,
    viewerReady,
    currentSceneMode,
    fetchVessels
  };
};

export default useVesselTracking;