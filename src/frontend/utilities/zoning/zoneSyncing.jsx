import axios from "axios";
import { convertCartesianToDegrees } from "../coordUtils";
import { toast } from "react-toastify";

const URL = window.location.href.split(":");

export const zyncGET = async (setNewZones, WebSocket) => {
  try {
    WebSocket.onopen = () => {
      // console.log("### getSharedZones: WebSocket connected from React");
    };
    WebSocket.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      // Ignore messages that aren't in Users topic, or if it doesn't contain a new zone
      if (!msg.topic.match("Users") || !msg.value.command.match('New Zone')) { 
        return () => WebSocket.close()};

      // console.log("### getSharedZones: Zones received");
      // console.log(msg);
      setNewZones((previousState) => new Set([
                ...previousState,
                JSON.stringify({
                    id: msg.value.id,
                    points: msg.value.points
                }),
          ]));
      };

    WebSocket.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    WebSocket.onclose = () => {
      console.log("WebSocket disconnected. Will no longer receive shared Zones");
    };

    // Return the full payload for use in zone entity description
    return () => WebSocket.close();
  } catch (error) {
    console.error("Error fetching shared zones:", error.message);
    toast.error("Zone sharing failure: Cannot receive shared zones.");
    return () => WebSocket.close();
  }
};

// TODO Execute rename and delete based on incoming command
export const receiveCMD = async (setGeometries, WebSocket) => {
    try {
        WebSocket.onopen = () => {
            console.log(
                // "### Connected to WebSocket and looking for incoming zoning commands...",
            );
        };
        WebSocket.onmessage = (event) => {
            // TODO: Filter out for commands
            const msg = JSON.parse(event.data);
            if (!msg.topic.match('Users') || !msg.value.command.match("DELETE")) {
                return () => Websocket.close();
            }
            console.log("### Incoming zoning Command");
            console.log(msg);
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

/* WARN:
 * I'm expecting possible activeZone.ID conflicts with other clients.
 * This will likely come in the form of the other clients not seeing the zone,
 * or the "Duplicate key error for children that caused vessel tracking to fail"
 *
 * I am not sure how to mitigate this. If we generate a new zoneID, we would have
 * to have the local zone ID updated in some way.
 */
export const zyncPOST = async (customZone, points, WebSocket) => {
  try {
    WebSocket.onopen = () => {
      // console.log("### ShareZone: WebSocket connected from React");
      WebSocket.send(
        JSON.stringify({
          topic: "Users",
          key: customZone.id,
          value: {
            command: "New Zone",
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
            // console.log("### Connected to WebSocket to send zoning commands...");
              WebSocket.send(
                JSON.stringify({
                    topic: "Users",
                    key: `${crypto.getRandomValues(new Uint32Array(1))[0]}`,
                    value: {
                        command: command,
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
