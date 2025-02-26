import { useEffect, useRef, useState } from "react";
import { Viewer, Entity, PolylineGraphics, PolygonGraphics, PointGraphics } from "resium";
import * as Cesium from "cesium";

const CustomGeometry = ({ isDrawing, shapeType, geometries, setGeometries, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings }) => {
    // const [showContextMenu, setShowContextMenu] = useState(false);
    // const [selectedGeometry, setSelectedGeometry] = useState(null);
    // const [contextMenuPosition, setContextMenuPosition] = useState({x: 0, y: 0});
    const viewerRef = useRef(null);

    // const createGeometry = (positions, name) => ({
    //     id: Date.now().toString(),
    //     positions,
    //     name: name || `Zone ${geometries.length + 1}`,
    //     shapeType,
    //     completed: false
    // });

    useEffect(() => {
        Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxZjRjZjA4Ny05YjE2LTQ4NWItOGJkNi04ZjkyZjJlZmExYTgiLCJpZCI6MjczMzkxLCJpYXQiOjE3Mzg3MDUzNzB9.Ur_w05dnvhyA0R13ddj4E7jtUkOXkmqy0G507nY0aos";
        console.log("Zoning tool active:", isDrawing);
        if (!viewerRef.current?.cesiumElement) return;

        const viewer = viewerRef.current.cesiumElement;
        viewer.scene.canvas.addEventListener("contextmenu", (e) => e.preventDefault());
        const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

        // Right-click context menu
        handler.setInputAction((click) => {
            console.log("Right-click detected");

            const pickedEntity = viewer.scene.pick(click.position);
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
            const pickedEntity = viewer.scene.pick(click.position);
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

            //Left click to start geometry 
            handler.setInputAction((click) => {
                console.log("Click event detected");
                // const cartesian = viewer.scene.pickPosition(click.position);
                let cartesian = viewer.scene.pickPosition(click.position);
                if (!cartesian) {
                    cartesian = viewer.scene.camera.pickEllipsoid(click.position, viewer.scene.globe.ellipsoid);
                }
                console.log("Posititon picked:", cartesian);
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

            // double click geometry complete
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
        } else {
            return;
        }


        return () => handler.destroy();
    }, [isDrawing, geometries, setSelectedGeometry, setShowContextMenu, setShowSettings]);

    return (
        <div className="cesium-container">
            <Viewer
                ref={viewerRef}
                className="cesium-viewer"
                animation={false}
                timeline={false}
                fullscreenButton={false}
                navigationHelpButton={false}
                homeButton={false}
                sceneModePicker={true}
                baseLayerPicker={true}
                geocoder={true}
            >
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
            </Viewer>
        </div>
    );
};

export default CustomGeometry;