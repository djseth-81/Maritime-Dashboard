import React, { useEffect, useImperativeHandle, useState, forwardRef } from "react";
import useRightClickContextMenu from "./hooks/useRightClickContextMenu";
import useLeftClickSelect from "./hooks/useLeftClickSelect";
import useDrawingHandler from "./hooks/useDrawingHandler";

/**
 * CustomGeometry component to handle geometry drawing and interaction in Cesium.
 * @param {Object} props - Component props.
 * @param {Object} props.viewer - Cesium viewer instance.
 * @param {boolean} props.viewerReady - Flag indicating if the viewer is ready.
 * @param {boolean} props.isDrawing - Flag indicating if drawing mode is active.
 * @param {Function} props.setSelectedGeometry - Function to set the selected geometry.
 * @param {Function} props.setShowContextMenu - Function to show or hide the context menu.
 * @param {Function} props.setContextMenuPosition - Function to set the context menu position.
 * @param {Function} props.setShowSettings - Function to show or hide settings.
 * @param {Array} props.geometries - Array of existing geometries.
 * @param {Function} props.setGeometries - Function to update the geometries state.
 * @returns {null}
 * @description This component sets up event handlers for drawing polygons and handling context menu interactions.
 * It uses custom hooks to manage the drawing state and interactions with the Cesium viewer.
 */

const CustomGeometry = forwardRef(({
    viewer,
    viewerReady,
    isDrawing,
    setSelectedGeometry,
    setShowContextMenu,
    setContextMenuPosition,
    setShowSettings,
    geometries,
    setGeometries,
}, ref) => {
    const [positions, setPositions] = useState([]);
    const [activeZone, setActiveZone] = useState(null);

    // Call hooks at the top level
    const scene = viewerReady && viewer?.current?.cesiumElement?.scene;
    
    useRightClickContextMenu(scene, setSelectedGeometry, setContextMenuPosition, setShowContextMenu);
    useLeftClickSelect(scene, setSelectedGeometry, setShowContextMenu, setShowSettings);
    useDrawingHandler(scene, isDrawing, positions, setPositions, viewer, geometries, setGeometries, activeZone, setActiveZone);

    // Function to undo the last point
    const undoLastPoint = () => {
        if (!scene) {
            console.log("Scene is not defined.");
            return;
        }
        if (!activeZone || positions.length === 0) {
            console.log("No active zone or points to undo.");
            return;
        }

        // Remove the last point from the active zone
        const updatedPoints = [...activeZone.points];
        const lastPoint = updatedPoints.pop(); // Get the last point entity
        if (lastPoint) {
            viewer.current.cesiumElement.entities.remove(lastPoint); // Remove the point entity from the viewer
            console.log("Removed point entity:", lastPoint.id);
        }

        // Update the positions and active zone
        setPositions((prevPositions) => {
            const newPositions = prevPositions.slice(0, -1); // Remove the last position
            if (newPositions.length === 0) {
                // Reset activeZone if no points remain
                setActiveZone(null);
                console.log("All points undone. Active zone reset.");
            } else {
                setActiveZone((prevZone) => ({
                    ...prevZone,
                    points: updatedPoints,
                }));
            }
            return newPositions;
        });
    };

    useImperativeHandle(ref, () => ({
        undoLastPoint,
    }));

    useEffect(() => {
        console.log("Active zone in CustomGeometry:", activeZone);
    }, [activeZone]);

    useEffect(() => {
        if (!scene) return;

        // Prevent default context menu
        scene.canvas.addEventListener("contextmenu", (e) => e.preventDefault());

        return () => {
            scene.canvas.removeEventListener("contextmenu", (e) => e.preventDefault());
        };
    }, [scene]);

    return null;
});

export default CustomGeometry;