import React from "react";
import { placeVessel } from "./Vessels";


/**
 * VesselTracking component to display vessels on the map.
 * @param {Object} props - Component props.
 * @param {Array} props.vessels - Array of vessel objects to be displayed.
 * @returns {JSX.Element} - The rendered VesselTracking component.
 * @description This component takes an array of vessel objects and places them on the map using the placeVessel function.
 */
const VesselTracking = React.memo(({ vessels }) => {
    // console.log("Vessels passed to VesselTracking:", vessels);
    return (
        <>
            {vessels.map((vessel) =>
                placeVessel(
                    vessel.mmsi,
                    vessel.lon,
                    vessel.lat,
                    vessel.heading,
                    vessel.elevation,
                    vessel.type,
                    vessel.vessel_name,
                    vessel.flag,
                    vessel.timestamp
                )
            )}
        </>
    );
});

export default VesselTracking;
