import React from 'react'
import { Entity } from 'resium'
import { Cartesian3, DistanceDisplayCondition, NearFarScalar, HeightReference } from 'cesium'
import ReactDOMServer from 'react-dom/server'
import BoatIcon from "../../assets/icons/boatIcon"

export function placeVessel(longitude, latitude, elevation, type="cargo", name="Vessel") {
  // Convert string values to numbers
  const numLongitude = Number(longitude);
  const numLatitude = Number(latitude);
  const numElevation = Number(elevation);

  // Validate coordinates and calculate position
  let position;
  if (isNaN(numLongitude) || isNaN(numLatitude) || isNaN(numElevation)) {
    console.warn(`Invalid coordinates for vessel ${name}:`, { longitude, latitude, elevation });
    position = Cartesian3.fromDegrees(0, 0, 0);
  } else {
    position = Cartesian3.fromDegrees(numLongitude, numLatitude, numElevation);
  }

  // Convert the BoatIcon SVG to a data URL
  const svgString = ReactDOMServer.renderToStaticMarkup(
    <BoatIcon type={type} size={50} />
  );
  
  // Create a properly formatted data URL
  const encodedSvg = encodeURIComponent(svgString);
  const dataUrl = `data:image/svg+xml;charset=utf-8,${encodedSvg}`;

  // For debugging - if SVG isn't working, use a simple colored circle
  // Uncomment this line to test with a simple colored pin
  //const dataUrl = "https://upload.wikimedia.org/wikipedia/commons/8/8c/Map_marker.svg";

  // Return the Entity component with the boat icon
  return (
    <Entity
      position={position}
      billboard={{
        image: dataUrl,
        scale: 0.5, 
        distanceDisplayCondition: new DistanceDisplayCondition(0, 20.0e6), // Reduced max distance
        scaleByDistance: new NearFarScalar(1.5e5, 1.5, 1.5e6, 0.5), // Adjusted scale ranges
        heightReference: HeightReference.CLAMP_TO_GROUND, // Keep vessels on surface
        verticalOrigin: 1, // CENTER
        horizontalOrigin: 0, // CENTER
        eyeOffset: new Cartesian3(0, 0, -500), // Offset to ensure visibility
        pixelOffset: new Cartesian3(0, 0, 0),
      }}
      name={`${type.charAt(0).toUpperCase() + type.slice(1)} Vessel: ${name}`}
      description={`This is a ${type} vessel named "${name}".`}
    />
  );
}