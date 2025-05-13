import { useEffect, useState, useCallback } from "react";
import { Ion } from "cesium";
/**
 * Custom hook to manage Cesium viewer lifecycle and scene mode change events.
 *
 * @param {Object} viewerRef - Reference to the Cesium viewer.
 * @param {Function} setViewerReady - Function to set the viewer ready state.
 * @returns {void}
 * @description This hook sets up an event listener for scene mode changes in the Cesium viewer.
 */

export const useCesiumViewer = (viewerRef, setViewerReady) => {
  const [scene, setScene] = useState(null);

  let token =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxZjRjZjA4Ny05YjE2LTQ4NWItOGJkNi04ZjkyZjJlZmExYTgiLCJpZCI6MjczMzkxLCJpYXQiOjE3Mzg3MDUzNzB9.Ur_w05dnvhyA0R13ddj4E7jtUkOXkmqy0G507nY0aos";
  Ion.defaultAccessToken = token;

  // Memoize the initializeScene function
  const initializeScene = useCallback(() => {
    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);
      setScene(viewer.scene);
    }
  }, [viewerRef, setViewerReady]);

  useEffect(() => {
    // Check if viewerRef.current is ready
    if (viewerRef.current) {
      initializeScene();
    }

    // Optionally, add a listener for when the Viewer is mounted
    const interval = setInterval(() => {
      if (viewerRef.current) {
        initializeScene();
        clearInterval(interval);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [viewerRef, initializeScene]);

  return scene;
};
