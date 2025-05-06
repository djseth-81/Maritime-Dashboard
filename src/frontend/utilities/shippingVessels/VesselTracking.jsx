import React from "react";
import { placeVessel } from "./Vessels";

const VesselTracking = React.memo(({ vessels }) => {
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
                ) || <div key={vessel.mmsi}>Invalid Vessel Data</div>
            )}
        </>
    );
});

export default VesselTracking;