import { useState, useEffect } from "react";
import { convertCartesianToDegrees } from "./coordUtils";

const ZoneSettingsUI = ({ zoneName, positions = [], onSave, onDelete, onRename }) => {
    const [isRenaming, setIsRenaming] = useState(false);
    const [newName, setNewName] = useState(zoneName);

    useEffect(() => {
        setNewName(zoneName);
    }, [zoneName]);

    const handleKeyPress = (e) => {
        if (e.key === "Enter") {
            onRename(newName);
            setIsRenaming(false);
        }
    };

    return (
        <div className="zone-settings-ui">
            <div className="settings-header">
                <h5>
                    Settings for zone '{zoneName}'
                    <button
                        className="rename-button"
                        onClick={() => setIsRenaming(true)}
                        title="Renaming Zone"
                    >
                        Rename
                    </button>
                </h5>
            </div>

            {isRenaming && (
                <div className="rename-section">
                    <input
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Edit zone name"
                        autoFocus
                    />
                    <button onClick={() => { onRename(newName); setIsRenaming(false); }}>
                        Save Name
                    </button>
                    <button onClick={() => setIsRenaming(false)}>Cancel</button>
                </div>
            )}

            <div className="settings-body">
                <h5>Coordinates:</h5>
                <ul>
                    {positions.map((pos, index) => {
                        const { latitude, longitude } = convertCartesianToDegrees(pos);
                        return (
                            <li key={index}>{`Lat: ${latitude.toFixed(6)}, Lon: ${longitude.toFixed(6)}`}</li>
                        );
                    })}
                </ul>
                <button className="save-btn" onClick={onSave}>Save</button>
                <button className="delete-btn" onClick={onDelete}>Delete</button>
            </div>
        </div>
    );
};

export default ZoneSettingsUI;