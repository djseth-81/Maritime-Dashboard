import React, { useEffect, useState } from 'react';
import { renderVesselEntity } from './Vessels';
import { SceneMode, Cartesian3, Cartographic, Math as CesiumMath } from 'cesium';

/**
 * Component that places a test boat on the map and reports its position
 * when the view mode changes
 */
const TestBoat = ({ viewer }) => {
  const [viewMode, setViewMode] = useState('3D');
  const [screenPosition, setScreenPosition] = useState({ x: 0, y: 0 });
  
  // Fixed test coordinates - using San Francisco Bay
  const testLongitude = -122.4194;
  const testLatitude = 37.7749;
  
  // Monitor scene mode changes
  useEffect(() => {
    if (!viewer?.current?.cesiumElement) return;
    
    const cesiumViewer = viewer.current.cesiumElement;
    
    const updateViewMode = () => {
      const scene = cesiumViewer.scene;
      let modeName = 'Unknown';
      
      switch(scene.mode) {
        case SceneMode.SCENE3D:
          modeName = '3D';
          break;
        case SceneMode.SCENE2D:
          modeName = '2D';
          break;
        case SceneMode.COLUMBUS_VIEW:
          modeName = 'Columbus';
          break;
      }
      
      setViewMode(modeName);
      
      // Track position of our test boat in screen coordinates and cartesian
      if (cesiumViewer.entities.values.length > 0) {
        const testEntity = cesiumViewer.entities.values.find(
          entity => entity.name === 'Cargo Vessel: Sample Boat'
        );
        
        if (testEntity && testEntity.position) {
          // Get position in scene's coordinate system
          const position = testEntity.position.getValue(cesiumViewer.clock.currentTime);
          
          if (position) {
            // Convert to screen coordinates
            const screenPos = cesiumViewer.scene.cartesianToCanvasCoordinates(position);
            if (screenPos) {
              setScreenPosition({ x: screenPos.x.toFixed(1), y: screenPos.y.toFixed(1) });
            }
            
            // Convert to lat/long and log
            const cartographic = Cartographic.fromCartesian(position);
            const longitudeDegrees = CesiumMath.toDegrees(cartographic.longitude);
            const latitudeDegrees = CesiumMath.toDegrees(cartographic.latitude);
            
            console.log(`Test boat in ${modeName} mode:`, {
              screenPosition: screenPos ? `X: ${screenPos.x.toFixed(1)}, Y: ${screenPos.y.toFixed(1)}` : 'Not visible',
              cartesianPosition: `X: ${position.x.toFixed(1)}, Y: ${position.y.toFixed(1)}, Z: ${position.z.toFixed(1)}`,
              geographicPosition: `Lon: ${longitudeDegrees.toFixed(4)}, Lat: ${latitudeDegrees.toFixed(4)}`
            });
          }
        } else {
          console.log("Test boat entity not found");
        }
      }
    };
    
    // Check immediately after a short delay to ensure entity is created
    setTimeout(updateViewMode, 1000);
    
    // Add listener for scene mode changes
    cesiumViewer.scene.morphComplete.addEventListener(updateViewMode);
    
    // Set up interval for periodic position logging
    const interval = setInterval(updateViewMode, 5000);
    
    return () => {
      if (cesiumViewer && !cesiumViewer.isDestroyed()) {
        cesiumViewer.scene.morphComplete.removeEventListener(updateViewMode);
        clearInterval(interval);
      }
    };
  }, [viewer]);
  
  return (
    <>
      {/* Place our test boat */}
      {renderVesselEntity(
        testLongitude,
        testLatitude,
        0,
        'cargo',
        'Sample Boat',
        viewer?.current?.cesiumElement
      )}
      
      {/* Display current view mode info */}
      <div style={{
        position: 'absolute',
        bottom: 10,
        left: 10,
        backgroundColor: 'rgba(0,0,0,0.7)',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        zIndex: 1000
      }}>
        <div>Test Boat Info:</div>
        <div>Mode: {viewMode}</div>
        <div>Longitude: {testLongitude}</div>
        <div>Latitude: {testLatitude}</div>
        <div>Screen Position: ({screenPosition.x}, {screenPosition.y})</div>
      </div>
    </>
  );
};

export default TestBoat;