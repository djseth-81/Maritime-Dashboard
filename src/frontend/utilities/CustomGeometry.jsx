import { useEffect, useState } from "react";
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

const CustomGeometry = ({
    viewer,
    viewerReady,
    isDrawing,
    setSelectedGeometry,
    setShowContextMenu,
    setContextMenuPosition,
    setShowSettings,
    geometries,
    setGeometries,
}) => {
    const [positions, setPositions] = useState([]);

    // Call hooks at the top level
    const scene = viewerReady && viewer?.current?.cesiumElement?.scene;

    // Check if the scene is ready
    if (!scene) return null;
    
    useRightClickContextMenu(scene, setSelectedGeometry, setContextMenuPosition, setShowContextMenu);
    useLeftClickSelect(scene, setSelectedGeometry, setShowContextMenu, setShowSettings);
    useDrawingHandler(scene, isDrawing, positions, setPositions, viewer, geometries, setGeometries);

    useEffect(() => {
        if (!scene) return;

        // Prevent default context menu
        scene.canvas.addEventListener("contextmenu", (e) => e.preventDefault());

        return () => {
            scene.canvas.removeEventListener("contextmenu", (e) => e.preventDefault());
        };
    }, [scene]);

    return null;
};

export default CustomGeometry;