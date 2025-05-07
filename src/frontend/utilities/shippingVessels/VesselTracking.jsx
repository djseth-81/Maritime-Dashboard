import React from "react";
import { placeVessel } from "./Vessels";

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
                    vessel.vessel_name
                )
            )}
        </>
    );
});

export default VesselTracking;
