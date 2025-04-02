import React from 'react'
import { Entity } from 'resium'
import { Cartesian3, DistanceDisplayCondition, NearFarScalar, HeightReference, SceneMode } from 'cesium'
import ReactDOMServer from 'react-dom/server'
import BoatIcon from "../../assets/icons/boatIcon"

export function placeVessel(longitude, latitude, heading, elevation = 0, type = "OTHER", name = "UNKOWN") {
    // Convert values to numbers and validate
    const numLongitude = Number(longitude);
    const numLatitude = Number(latitude);
    const numElevation = Number(elevation);

    if (isNaN(numLongitude) || isNaN(numLatitude)) {
        console.warn(`Invalid coordinates for vessel "${name}":`, {
            longitude, latitude, elevation
        });
        return null;
    }

    // Get current scene mode if viewer is provided
    let currentSceneMode = viewer?.scene?.mode;
    
    // Debug: Log coordinates and scene mode for this entity
    console.log(`Rendering vessel ${name} at (${numLongitude}, ${numLatitude}) in mode: ${getSceneModeName(currentSceneMode)}`);
    
    // Create a unique key that includes scene mode to force re-creation when mode changes
    const entityKey = `${name}-${longitude}-${latitude}-${currentSceneMode || 'default'}`;

    // Initialize billboard properties
    let scale = 2.0;
    let heightReference = HeightReference.CLAMP_TO_GROUND;
    let position;
    let billboardOptions = {};

    // Create position and set properties based on scene mode for better accuracy
    if (currentSceneMode === SceneMode.SCENE2D) {
        // For 2D mode, set elevation to a small positive value to prevent z-fighting
        position = Cartesian3.fromDegrees(numLongitude, numLatitude, 10);
        scale = 1.5; // Smaller in 2D mode
        heightReference = HeightReference.NONE; // Don't clamp in 2D
        
    } else if (currentSceneMode === SceneMode.COLUMBUS_VIEW) {
        // Columbus view needs special handling for height
        position = Cartesian3.fromDegrees(numLongitude, numLatitude, 5);
        scale = 1.8; // Medium size in Columbus view
        HeightReference.None
    } else {
        // 3D mode - use the provided elevation if available
        position = Cartesian3.fromDegrees(numLongitude, numLatitude, numElevation);
        scale = 2.0;
        heightReference = numElevation > 0 ? HeightReference.NONE : HeightReference.CLAMP_TO_GROUND;
    }
    
    // Generate the SVG icon
    const svgString = ReactDOMServer.renderToStaticMarkup(
        <BoatIcon type={type} size={25} heading={heading} />
    );

    const encodedSvg = encodeURIComponent(svgString);
    const dataUrl = `data:image/svg+xml;charset=utf-8,${encodedSvg}`;

    // Combine common billboard properties with mode-specific ones
    const billboardProps = {
        image: dataUrl,
        scale: scale,
        distanceDisplayCondition: new DistanceDisplayCondition(0, 20.0e6),
        scaleByDistance: new NearFarScalar(1.5e5, 1.5, 1.5e6, 0.5),
        heightReference: heightReference,
        verticalOrigin: 1,
        horizontalOrigin: 0,
        eyeOffset: new Cartesian3(0, 0, -500),
        pixelOffset: new Cartesian3(0, 0, 0),
        ...billboardOptions
    };

    return (
        <Entity
            key={entityKey}
            position={position}
            billboard={{
                image: dataUrl,
                scale: 2.0,
                distanceDisplayCondition: new DistanceDisplayCondition(0, 20.0e6),
                scaleByDistance: new NearFarScalar(1.5e5, 1.5, 1.5e6, 0.5),
                heightReference: HeightReference.None,
                verticalOrigin: 1,
                horizontalOrigin: 0,
                eyeOffset: new Cartesian3(0, 0, -500),
                pixelOffset: new Cartesian3(0, 0, 0),
            }}
            name={`${type.charAt(0).toUpperCase() + type.slice(1)} Vessel: ${name}`}
            description={`This is a ${type} vessel named "${name}" at position ${numLongitude.toFixed(4)}, ${numLatitude.toFixed(4)}`}
        />
    );
}

// Helper function to get scene mode name for logging
function getSceneModeName(sceneMode) {
    switch(sceneMode) {
        case SceneMode.SCENE3D: return "3D";
        case SceneMode.SCENE2D: return "2D";
        case SceneMode.COLUMBUS_VIEW: return "Columbus View";
        default: return "Unknown";
    }
}