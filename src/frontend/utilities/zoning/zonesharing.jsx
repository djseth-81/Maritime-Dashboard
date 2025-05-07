import axios from "axios";
import { convertCartesianToDegrees } from "../coordUtils";
import { toast } from "react-toastify";

const URL = window.location.href.split(":");

// TODO: Update geometries with appending geometry and ID, so long as ID is unique
export const getSharedZones = async (setGeometries, WebSocket) => {
  try {
    WebSocket.onopen = () => {
      console.log("### getSharedZones: WebSocket connected from React");
    };
    WebSocket.onmessage = (event) => {
      console.log("### getSharedZones: Zones received");
      console.log(event.data);
    };
    WebSocket.onerror = (err) => {
      console.error("### getSharedZones: WebSocket error:", err);
    };

    WebSocket.onclose = () => {
      console.log("### getSharedZones: WebSocket disconnected");
    };

    // mimic this to add zones found shared to geometries array
    // const transformedVessels = response.data.payload.vessels?.map((vessel) =>
    //   Array.isArray(vessel)
    //     ? {
    //         mmsi: vessel["mmsi"],
    //         name: vessel["vessel_name"],
    //         type: vessel["type"],
    //         country_of_origin: vessel["flag"],
    //         status: vessel["current_status"],
    //         latitude: vessel["lat"],
    //         longitude: vessel["lon"],
    //       }
    //     : vessel
    // );

    // // Only update vessels state if setVessels function was provided
    // if (setVessels) {
    //   setVessels(transformedVessels);
    // }

    // Append shared geometries
    // setGeometries((prevGeometries) => [
    //   ...prevGeometries,
    //   { // Ask about the difference between positions and points
    //     id: activeZone.id,
    //     entity: activeZone.entity,
    //     positions: [...positions],
    //     points: activeZone.points,
    //     show: true,
    //   },
    // ]);

    // Return the full payload for use in zone entity description
    return () => WebSocket.close();
  } catch (error) {
    console.error("Error fetching shared zones:", error.message);
    toast.error("Zone sharing failure: Cannot receive shared zones.");
    return () => WebSocket.close();
  }
};

/* WARN:
 * I'm expecting possible activeZone.ID conflicts with other clients.
 * This will likely come in the form of the other clients not seeing the zone,
 * or the "Duplicate key error for children that caused vessel tracking to fail"
 *
 * I am not sure how to mitigate this. If we generate a new zoneID, we would have
 * to have the local zone ID updated in some way.
 */
export const shareZone = async (customZone, points, WebSocket) => {
  try {
    WebSocket.onopen = () => {
      console.log("### ShareZone: WebSocket connected from React");
      WebSocket.send(
        JSON.stringify({
          topic: "Users",
          key: customZone.id,
          payload: {
            message: "New custom zone to share",
            id: customZone.id,
            points: points
          }
        }),
      );
    };
    WebSocket.onerror = (err) => {
      console.error("### ShareZone: Unable to share custom zone:", err);
    };

    WebSocket.onclose = () => {
      console.log("### ShareZone: WebSocket disconnected");
    };

    return () => WebSocket.close();
  } catch (error) {
    console.error("Error sharing zones:", error.message);
    toast.error("Zone sharing failure: Unable to share zone.");
    return () => WebSocket.close();
  }
};

// TODO Format commands for rename and delete
export const sendCMD = async (command, ids=null, data=null, WebSocket) => {
    try {
        WebSocket.onopen = () => {
            console.log("### Connected to WebSocket to send zoning commands...");
              WebSocket.send(
                JSON.stringify({
                    topic: "Users",
                    key: `${crypto.getRandomValues(new Uint32Array(1))[0]}`,
                    payload: {
                        message: command,
                        ids: ids,
                        data: data
                    }
                }));
        };

        WebSocket.onerror = (err) => {
            console.error("### Error sending zoning commands:", err);
        };

        WebSocket.onclose = () => {
            console.log(
                "### WebSocket disconnected. Will no longer submit zoning commands",
            );
        };

        return () => WebSocket.close();
    } catch (error) {
        console.error("Error sharing zones:", error.message);
        toast.error("Zone sharing failure: Unable to share zone.");
        return () => WebSocket.close();
    }
};

// TODO Execute rename and delete based on incoming command
export const receiveCMD = async (WebSocket) => {
    try {
        WebSocket.onopen = () => {
            console.log(
                "### Connected to WebSocket and looking for incoming zoning commands...",
            );
        };
        WebSocket.onmessage = (event) => {
            // TODO: Filter out for commands
            console.log("### Incoming zoning Command");
            console.log(event.data);
        };
        WebSocket.onerror = (err) => {
            console.error("### Error looking for incoming zoning commands:", err);
        };

        WebSocket.onclose = () => {
            console.log(
                "### WebSocket disconnected. Will no longer receive incoming zoning commands",
            );
        };

        return () => WebSocket.close();
    } catch (error) {
        console.error("Error sharing zones:", error.message);
        toast.error("Zone sharing failure: Unable to share zone.");
        return () => WebSocket.close();
    }
};
