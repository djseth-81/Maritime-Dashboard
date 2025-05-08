// import { useMemo }  from "react";
import axios from "axios";
import * as Cesium from "cesium";
import { convertCartesianToDegrees } from "../coordUtils";
import { toast } from "react-toastify";
import { generateZoneDescription } from "./ZoneInfobox";

const URL = window.location.href.split(":");

// TODO: Update geometries with appending geometry and ID, so long as ID is unique
export const getSharedZones = async (setNewZones, WebSocket) => {

  try {
    WebSocket.onopen = () => {
      console.log("### getSharedZones: WebSocket connected from React");
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

export const updateZones = (scene, viewer, geometries, newZones, setGeometries) => {
    const isEqual = (arr1, arr2) => {
        if (arr1.length !== arr2.length) return false;
        let a = arr1.map(x => JSON.stringify(x));
        let b = arr2.map(y => JSON.stringify(y));
        return a.every((i) => b.indexOf(i) !== -1);
   };

    console.log("### Zones to process");
    console.log(newZones.size);
    console.log(newZones);

    let pending = [];
    let unique = [];
    newZones.forEach((zone) => pending.push(JSON.parse(zone)));
    // console.log(pending);

    pending.forEach((item) => {
        // console.log(`Shared zone: ${item.id}`);
        geometries.some((geom) => {
            // console.log(`Pre-exisitng zone: ${geom.id}`);
            // console.log(`ID match? ${geom.id === item.id}`)
            // console.log(`Verticies match? ${isEqual(item.points, geom.positions)}`);
            if ((geom.id === item.id) && (isEqual(item.points, geom.positions))) {
                console.log("Geometry already exists!");
            } else if ((geom.id !== item.id) && (isEqual(item.points, geom.positions))) {
                console.log("Geom exists, but is under a different ID");
            } else {
                console.log("No pre-existing geometry");
                unique.push(item);
            }
        });
    });
    console.log("Unique geometries found:");
    console.log(unique);

    // unique.forEach((item) => {
    //   // Defining positions array to append to later when going through reported verticies
    //   let pts = [];
    //   item.points.forEach((pt) => {
    //         console.log(`pt being processed: ${pt}`);
    //         const cartesian = new Cesium.Cartesian3(pt.x, pt.y, pt.z)
    //         console.log(`new cartesian point off pt: ${cartesian}`);
    //         const pointEntity = viewer.current.cesiumElement.entities.add({
    //           position: cartesian,
    //           point: {
    //             pixelSize: 10,
    //             color: Cesium.Color.RED,
    //             outlineColor: Cesium.Color.WHITE,
    //             outlineWidth: 2,
    //           },
    //           name: `Point ${pos.length + 1}`,
    //           label: {
    //             text: `Point ${pos.length + 1}`,
    //             font: "14px Helvetica",
    //             scale: 0.8,
    //             pixelOffset: labelOffset,
    //           },
    //           parent: zoneEntity,
    //         });
    //         pos.push(cartesian);
    //         activeZone.points.push(pointEntity);
    //   });

    //   // Defining label offset
    //   const labelOffset = (() => new Cesium.Cartesian2(0, -20), []);

    //   // Create new zone entity for item
    //   const zoneEntity = viewer.current.cesiumElement.entities.add({
    //     polygon: {
    //       hierarchy: new Cesium.PolygonHierarchy([]),
    //       material: Cesium.Color.RED.withAlpha(0.5),
    //     },
    //     name: `Zone ${geometries.length + 1}`,
    //     isGeometry: true,
    //   });

    //   // Create new active zone for item, and assigning it reported ID and zoneEntity object
    //   const activeZone = {
    //     id: item.id,
    //     entity: zoneEntity,
    //     points: [],
    //   };

    //     // I think at this point the click event records a position to
    //     // append to Point and positions, so let's iterate through the verticies we do have

    //     activeZone.entity.polygon.hierarchy = new Cesium.PolygonHierarchy(
    //         pos
    //     );

    //     if (!activeZone.entity.description) {
    //         activeZone.entity.description = generateZoneDescription(
    //             activeZone.entity.name,
    //             null
    //         );
    //     }

    //     console.log("Zones details to add:");
    //     console.log(`id: ${activeZone.id} (${typeof(activeZone.id)})`)
    //     console.log(`pos: ${pos} (${typeof(pos)})`)

    //     setGeometries((prevGeoms) => [
    //             ...prevGeoms,
    //             {
    //                 id : activeZone.id,
    //                 entity: activeZone.entity,
    //                 positions : [...pos],
    //                 show : true,
    //             },
    //     ]);

    //     console.log("New zone added!");
    //     console.log(activeZone.id);
    //     console.log(activeZone.positions);
    //     unique.pop(item);

    // });

};

// TODO Execute rename and delete based on incoming command
export const receiveCMD = async (setGeometries, WebSocket) => {
    try {
        WebSocket.onopen = () => {
            console.log(
                "### Connected to WebSocket and looking for incoming zoning commands...",
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
export const shareZone = async (customZone, points, WebSocket) => {
  try {
    WebSocket.onopen = () => {
      console.log("### ShareZone: WebSocket connected from React");
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
            console.log("### Connected to WebSocket to send zoning commands...");
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
