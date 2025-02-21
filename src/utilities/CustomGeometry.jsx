import { useEffect, useRef } from "react";
import { Viewer, Entity, PolylineGraphics, PolygonGraphics, PointGraphics } from "resium";
import * as Cesium from "cesium";

const CustomGeometry = ({ isDrawing, shapeType, geometries, setGeometries }) => {
    const viewerRef = useRef(null);

    useEffect(() => {
        Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxZjRjZjA4Ny05YjE2LTQ4NWItOGJkNi04ZjkyZjJlZmExYTgiLCJpZCI6MjczMzkxLCJpYXQiOjE3Mzg3MDUzNzB9.Ur_w05dnvhyA0R13ddj4E7jtUkOXkmqy0G507nY0aos";

        if (!viewerRef.current || !isDrawing) return;

        const viewer = viewerRef.current.cesiumElement;
        const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);

        handler.setInputAction((click) => {
            const cartesian = viewer.scene.pickPosition(click.position);
            if (cartesian) {
                setGeometries((prev) => {
                    if (prev.length === 0 || prev[prev.length - 1].completed) {
                        return [...prev, { shapeType, positions: [cartesian], completed: false }];
                    } else {
                        const updated = [...prev];
                        updated[updated.length - 1].positions.push(cartesian);
                        return updated;
                    }
                });
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        handler.setInputAction(() => {
            setGeometries((prev) => {
                if (prev.length === 0) return prev;
                const updated = [...prev];
                updated[updated.length - 1].completed = true;
                return updated;
            });
        }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);
        
        return () => handler.destroy();
    }, [isDrawing]);

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
                baseLayerPicker={false}
                geocoder={false}
            >
                {geometries.map((geometry, index) => (
                    <Entity key={index}>
                        {geometry.shapeType === "polyline" && (
                            <PolylineGraphics positions={geometry.positions} material={Cesium.Color.RED} width={3} />
                        )}
                        {geometry.shapeType === "polygon" && (
                            <PolygonGraphics
                                hierarchy={new Cesium.PolygonHierarchy(geometry.position)}
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