import React, { useEffect, useState } from 'react';
import { placeVessel } from './Vessels';
import { SceneMode } from 'cesium';

/**
 * Component that places a test boat on the map and reports its position
 * when the view mode changes
 */
const TestBoat = ({ viewer }) => {
  const [viewMode, setViewMode] = useState('3D');
  
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
      
      // Log the current position of our test boat in screen coordinates
      // This helps determine if it's moved on screen
      if (cesiumViewer.entities.values.length > 0) {
        const testEntity = cesiumViewer.entities.values.find(
          entity => entity.name === 'Tankers Vessel: Sample Boat'
        );
        
        if (testEntity && testEntity.position) {
          const position = testEntity.position.getValue(cesiumViewer.clock.currentTime);
          if (position) {
            const screenPosition = cesiumViewer.scene.cartesianToCanvasCoordinates(position);
            console.log(`Test boat screen position in ${modeName} mode:`, 
              screenPosition ? `X: ${screenPosition.x}, Y: ${screenPosition.y}` : 'Not visible');
          }
        }
      }
    };
    
    // Initial check
    // Use a timeout to ensure the viewer is fully initialized
    setTimeout(updateViewMode, 1000);
    
    // Add listener for scene mode changes
    cesiumViewer.scene.morphComplete.addEventListener(updateViewMode);
    
    return () => {
      if (cesiumViewer && !cesiumViewer.isDestroyed()) {
        cesiumViewer.scene.morphComplete.removeEventListener(updateViewMode);
      }
    };
  }, [viewer]);
  
  return (
    <>
      {/* Place our test boat */}
      {placeVessel(
        testLongitude,
        testLatitude,
        0,
        'tankers',
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
        <div>Test Boat Mode: {viewMode}</div>
        <div>Longitude: {testLongitude}</div>
        <div>Latitude: {testLatitude}</div>
      </div>
    </>
  );
};

export default TestBoat;