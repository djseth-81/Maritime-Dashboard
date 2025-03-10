import { useEffect } from "react";
import { Entity, PolylineGraphics, PolygonGraphics, PointGraphics } from "resium";
import * as Cesium from "cesium";

const CustomGeometry = ({ viewer, viewerReady, isDrawing, shapeType, geometries, setGeometries, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings }) => {
    useEffect(() => {
        console.log("Zoning tool active:", isDrawing);
        if (!viewerReady || !viewer.current?.cesiumElement) return;

        const scene = viewer.current.cesiumElement.scene;

        // Disables native browser context menu.
        scene.canvas.addEventListener("contextmenu", (e) => e.preventDefault());

        const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

        // Right-click context menu
        handler.setInputAction((click) => {
            console.log("Right-click detected");

            const pickedEntity = scene.pick(click.position);
            console.log("Right Click: Entity selected", pickedEntity);
            if (Cesium.defined(pickedEntity)) {
                setSelectedGeometry(pickedEntity);
                setContextMenuPosition({ x: click.position.x, y: click.position.y });
                setShowContextMenu(true);
            } else {
                setShowContextMenu(false);
            }
        }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

        // Left-click to select entities (geometries ATM)
        handler.setInputAction((click) => {
            const pickedEntity = scene.pick(click.position);
            console.log("Left-click: Entity selected.", pickedEntity);
            if (Cesium.defined(pickedEntity)) {
                setSelectedGeometry(pickedEntity);
            } else {
                console.log("Deselected geometry");
                setShowContextMenu(false);
                setShowSettings(false);
                setSelectedGeometry(null);
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        if (isDrawing) {
            // Left click to start geometry
            handler.setInputAction((click) => {
                console.log("Click event detected");
                let cartesian = scene.pickPosition(click.position);
                if (!cartesian) {
                    cartesian = scene.camera.pickEllipsoid(click.position, scene.globe.ellipsoid);
                }
                console.log("Position picked:", cartesian);
                if (cartesian) {
                    setGeometries((prev) => {
                        console.log("Current geometries: ", prev);
                        if (prev.length === 0 || prev[prev.length - 1].completed) {
                            const newZoneName = `Zone ${prev.length + 1}`;
                            console.log("Creating new geometry");
                            return [...prev, { shapeType, positions: [cartesian], completed: false, name: newZoneName }];
                        } else {
                            console.log("Adding point to existing geometry");
                            const updated = [...prev];
                            updated[updated.length - 1].positions.push(cartesian);
                            return updated;
                        }
                    });
                }
            }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

            // Double click to complete geometry
            handler.setInputAction(() => {
                console.log("Left-double-click detected, completing geometry.");
                setGeometries((prev) => {
                    if (prev.length === 0) return prev;
                    const updated = [...prev];
                    updated[updated.length - 1].completed = true;
                    console.log("Updated geometries after completion:", updated);
                    return updated;
                });
            }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
        }

        return () => {
            handler.destroy();
        };
    }, [viewer, viewerReady, isDrawing, shapeType, setGeometries, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings]);

    return (
        <div>
            {geometries.map((geometry, index) => (
                <Entity key={index}>
                    {geometry.shapeType === "polyline" && (
                        <PolylineGraphics positions={geometry.positions} material={Cesium.Color.RED} width={3} />
                    )}
                    {geometry.shapeType === "polygon" && (
                        <PolygonGraphics
                            hierarchy={new Cesium.PolygonHierarchy(geometry.positions)}
                            material={Cesium.Color.RED.withAlpha(0.5)}
                        />
                    )}
                    {geometry.shapeType === "point" &&
                        geometry.positions.map((pos, i) => (
                            <Entity key={i} position={pos}>
                                <PointGraphics pixelSize={10} color={Cesium.Color.BLACK} />
                            </Entity>
                        ))}
                </Entity>
            ))}
        </div>
    );
};

export default CustomGeometry;