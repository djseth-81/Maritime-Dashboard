import { useEffect, useRef } from "react";
import * as Cesium from "cesium";
import { convertCartesianToDegrees } from "../coordUtils";

/**
 * Custom hook to handle drawing polygons on a Cesium scene.
 * @param {Object} scene - The Cesium scene object.
 * @param {boolean} isDrawing - Flag to indicate if drawing mode is active.
 * @param {Array} positions - Array of positions for the polygon.
 * @param {Function} setPositions - Function to update the positions state.
 * @param {Object} viewer - The Cesium viewer object.
 * @param {Array} geometries - Array of existing geometries.
 * @param {Function} setGeometries - Function to update the geometries state.
 * @returns {void}
 * @description This hook sets up event handlers for drawing polygons on the Cesium canvas.
 * It handles left-click for adding points and double-click for completing the polygon.
 */

const useDrawingHandler = (scene, isDrawing, positions, setPositions, viewer, geometries, setGeometries) => {
    const lastClickTimeRef = useRef(0);
    const doubleClickDetectedRef = useRef(false);

    useEffect(() => {
        if (!scene || !isDrawing) return;

        const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

        // Left-click to draw
        handler.setInputAction((click) => {
            const currentTime = Date.now();

            if (currentTime - lastClickTimeRef.current < 300) {
                // Double left-click detected
                doubleClickDetectedRef.current = true;
                return;
            }

            doubleClickDetectedRef.current = false;
            lastClickTimeRef.current = currentTime;

            setTimeout(() => {
                if (!doubleClickDetectedRef.current) {
                    let cartesian = scene.pickPosition(click.position);
                    if (!cartesian) {
                        cartesian = scene.camera.pickEllipsoid(click.position, scene.globe.ellipsoid);
                    }
                    console.log("Drawing left-click registered at position:", click.position, "Cartesian:", cartesian);
                    if (cartesian) {
                        const { latitude, longitude } = convertCartesianToDegrees(cartesian);
                        console.log("Converted coordinates:", { latitude, longitude });

                        /**
                         * Add a point primitive to the scene for visual feedback.
                         */
                        const pointPrimitives = viewer.current.cesiumElement.scene.primitives.add(
                            new Cesium.PointPrimitiveCollection()
                        );
                        pointPrimitives.add({
                            position: cartesian,
                            pixelSize: 10,
                            color: Cesium.Color.RED,
                            outlineColor: Cesium.Color.WHITE,
                            outlineWidth: 2,
                        });
                        
                        setPositions((prevPositions) => [...prevPositions, cartesian]);
                    }
                }
            }, 300);
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        // Double-click to complete geometry
        handler.setInputAction(() => {
            console.log("Double-click registered to complete geometry");
            if (positions.length > 2) {
                const newPolygon = viewer.current.cesiumElement.entities.add({
                    polygon: {
                        hierarchy: new Cesium.PolygonHierarchy(positions),
                        material: Cesium.Color.RED.withAlpha(0.5),
                    },
                    name: `Zone ${geometries.length + 1}`,
                    isGeometry: true, // Add custom property to identify geometry
                });

                setGeometries((prevGeometries) => [
                    ...prevGeometries,
                    { id: newPolygon.id, positions: [...positions] },
                ]);

                setPositions([]); // Resets positions for next polygon
            }

            // Reset the double-click flag after handling the double-click
            setTimeout(() => {
                doubleClickDetectedRef.current = false;
            }, 300);
        }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);

        return () => {
            handler.destroy();
        };
    }, [scene, isDrawing, positions, setPositions, viewer, setGeometries]);
};

export default useDrawingHandler;