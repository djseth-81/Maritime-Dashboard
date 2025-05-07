import React from 'react'
import { Entity } from 'resium'
import { Cartesian3, DistanceDisplayCondition, NearFarScalar, HeightReference } from 'cesium'
import ReactDOMServer from 'react-dom/server'
import BoatIcon from "../../assets/icons/boatIcon";

export function placeVessel(mmsi, longitude, latitude, heading, elevation = 0, type = "OTHER", name = "UNKNOWN", timestamp) {
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

    const position = Cartesian3.fromDegrees(numLongitude, numLatitude, numElevation);

    const svgString = ReactDOMServer.renderToStaticMarkup(
        <BoatIcon type={type} size={25} heading={heading} />
    );

    const encodedSvg = encodeURIComponent(svgString);
    const dataUrl = `data:image/svg+xml;charset=utf-8,${encodedSvg}`;

    // Create a fully custom HTML description with inline styles
    const description = `
        <div style="background-color:#1a1a1a; color:#ffffff; font-family:Arial; padding:10px; margin:-10px; width:calc(100% + 20px);">
            <h3 style="margin-top:0; color:#ffffff;">${type} Details</h3>
            <table style="width:100%; color:#ffffff;">
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">Name:</td>
                    <td style="color:#ffffff; padding:3px 0;"><strong>${name}</strong></td>
                </tr>
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">MMSI:</td>
                    <td style="color:#ffffff; padding:3px 0;"><strong>${mmsi}</strong></td>
                </tr>
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">Type:</td>
                    <td style="color:#ffffff; padding:3px 0;">${type}</td>
                </tr>
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">Position:</td>
                    <td style="color:#ffffff; padding:3px 0;">${numLatitude.toFixed(4)}°, ${numLongitude.toFixed(4)}°</td>
                </tr>
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">Heading:</td>
                    <td style="color:#ffffff; padding:3px 0;">${heading}°</td>
                </tr>
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">Last updated:</td>
                    <td style="color:#ffffff; padding:3px 0;">${timestamp}</td>
                </tr>
                <tr>
                    <td style="color:#ffffff; padding:3px 0;">Last updated:</td>
                    <td style="color:#ffffff; padding:3px 0;">${flag}</td>
                </tr>
            </table>
        </div>
    `;

    return (
        <Entity
            key={`${mmsi}`}
            position={position}
            billboard={{
                image: dataUrl,
                scale: 1.5,
                distanceDisplayCondition: new DistanceDisplayCondition(0, 20.0e6),
                scaleByDistance: new NearFarScalar(1.5e5, 1.5, 1.5e6, 0.5),
                heightReference: HeightReference.None,
                verticalOrigin: 1,
                horizontalOrigin: 0,
                eyeOffset: new Cartesian3(0, 0, -500),
                pixelOffset: new Cartesian3(0, 0, 0),
            }}
            name={`${type.charAt(0).toUpperCase() + type.slice(1)} Vessel: ${name}`}
            description={description}
        />
    );
}
