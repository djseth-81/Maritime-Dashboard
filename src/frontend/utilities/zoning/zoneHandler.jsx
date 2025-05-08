import * as Cesium from "cesium";
import { generateZoneDescription } from "./ZoneInfobox";

export const updateZones = (scene, viewer, geometries, newZones, setGeometries) => {
    const isEqual = (arr1, arr2) => {
        if (arr1.length !== arr2.length) return false;
        let a = arr1.map(x => JSON.stringify(x));
        let b = arr2.map(y => JSON.stringify(y));
        return a.every((i) => b.indexOf(i) !== -1);
   };

    let pending = [];
    let unique = [];


    if (newZones.size === 0) return;

    newZones.forEach((zone) => pending.push(JSON.parse(zone)));
    console.log("### Incoming zones:");
    console.log(pending);

    console.log(`${geometries.length} Pre-existing Geometries:`)
    let geom_ids = geometries.map((geom) => geom.id);
    console.log(geom_ids);

    if (geometries.length > 0) { // If zones are already drawn, compare
        pending.forEach((item) => {
            console.log(`ID exist in geometries? ${geom_ids.indexOf(item.id) !== -1}`);
            if (geom_ids.indexOf(item.id) === -1) {unique.push({id: item.id, points: item.points});}
        });
    } else { // Otherwise, assume they're all unique
        pending.forEach((item) => unique.push({id: item.id, points: item.points}));
    }

    console.log("Unique geometries to process:");
    console.log(unique);

    // Now, go through and process unique items
    unique.forEach((item) => {
      // Defining label offset
      const labelOffset = new Cesium.Cartesian2(0, -20);

      // Defining positions array to append to later when going through reported verticies
      let pts = []; // positions
      let dots = []; // Points

      // Create new zone entity for item
      const zoneEntity = viewer.current.cesiumElement.entities.add({
        polygon: {
          hierarchy: new Cesium.PolygonHierarchy([]),
          material: Cesium.Color.RED.withAlpha(0.5),
        },
        name: `Zone ${geometries.length + 1}`,
        isGeometry: true,
      });

      // Create new active zone for item, and assigning it reported ID and zoneEntity object
      const activeZone = {
        id: item.id,
        entity: zoneEntity,
        points: [],
      };

      // I think at this point the click event records a position to
      // append to Point and positions, so let's iterate through the verticies we do have
      item.points.forEach((pt) => {
            // console.log(`pt being processed: ${pt}`);
            const cartesian = new Cesium.Cartesian3(pt.x, pt.y, pt.z)
            // console.log(`new cartesian point off pt: ${cartesian}`);
            const pointEntity = viewer.current.cesiumElement.entities.add({
              position: cartesian,
              point: {
                pixelSize: 10,
                color: Cesium.Color.RED,
                outlineColor: Cesium.Color.WHITE,
                outlineWidth: 2,
              },
              name: `Point ${pts.length + 1}`,
              label: {
                text: `Point ${pts.length + 1}`,
                font: "14px Helvetica",
                scale: 0.8,
                pixelOffset: labelOffset,
              },
              parent: zoneEntity,
            });
            pts.push(cartesian);
            activeZone.points.push(pointEntity);
      });


        activeZone.entity.polygon.hierarchy = new Cesium.PolygonHierarchy(
           pts 
        );

        if (!activeZone.entity.description) {
            activeZone.entity.description = generateZoneDescription(
                activeZone.entity.name,
                null
            );
        }

        setGeometries((prevGeoms) => [
                ...prevGeoms,
                {
                    id : activeZone.id,
                    entity: activeZone.entity,
                    positions : [...pts],
                    points: activeZone.points,
                    show : true
                },
        ]);

        console.log(`Shared zone Drawn: ${geometries.find((geom) => geom.id === activeZone.id)}`);

        unique.pop(item);
        console.log("Zones left to process:");
        console.log(unique.length);
    });

    return;

};
