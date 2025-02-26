import { useState } from "react";

const ToolsUI = ({ onToggleDrawing, onUndo, onClear, onSelectShape }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedShape, setSelectedShape] = useState("polygon");

    const handleShapeChange = (event) => {
        setSelectedShape(event.target.value);
        onSelectShape(event.target.value);
    };

    return (
        <div style={{ position: "absolute", top: 10, left: 10, zIndex: 1000 }}>
            {/*Button to expand/collapse sidebar*/}
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    padding: "10px",
                    backgroundColor: "#333",
                    color: "#fff",
                    border: "none",
                    cursor: "pointer",
                }}
            >
                {isOpen ? "Close" : "Tools"}
            </button>

            {/* Sidebar Content */}
            {isOpen && (
                <div
                    style={{
                        backgroundColor: "rgba(255,255,255,0.9)",
                        padding: "10px",
                        borderRadius: "5px",
                        marginTop: "5px",
                    }}
                >
                    <h4>Zoning Tools</h4>

                    <button onClick={onToggleDrawing}>Toggle Zoning Tool</button>
                    <button onClick={onUndo}>Undo</button>
                    <button onClick={onClear}>Clear</button>

                    <h4>Select Shape</h4>
                    <label>
                        <input
                            type="radio"
                            value="polygon"
                            checked={selectedShape === "polygon"}
                            onChange={handleShapeChange}
                        />
                        Polygon
                    </label>
                    <label>
                        <input
                            type="radio"
                            value="polyline"
                            checked={selectedShape === "polyline"}
                            onChange={handleShapeChange}
                        />
                        Polyline
                    </label>
                    <label>
                        <input
                            type="radio"
                            value="point"
                            checked={selectedShape === "point"}
                            onChange={handleShapeChange}
                        />
                        Point
                    </label>
                </div>
            )}
        </div>
    );
};

export default ToolsUI;