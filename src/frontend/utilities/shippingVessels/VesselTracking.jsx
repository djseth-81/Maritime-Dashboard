import React from "react";
import { placeVessel } from "./Vessels";

const VesselTracking = React.memo(({ vessels }) => {
    return (
        <>
            {vessels.map((vessel) => {
              placeVessel(
                vessel.mmsi,
                vessel.longitude,
                vessel.latitude,
                vessel.heading,
                vessel.elevation,
                vessel.type,
                vessel.name)
            })}
        </>
    );
});

export default VesselTracking;