import { useState } from "react";

const ZoneSettings = ({ zoneName, onSave, onDelete, onRename }) => {
    const [isRenaming, setIsRenaming] = useState(false);
    const [newName, setNewName] = useState(zoneName);

    const handleKeyPress = (e) => {
        if (e.key === "Enter") {
            onRename(newName);
            setIsRenaming(false);
        }
    };

    return (
        <div className="zone-settings-ui">
            <div className="settings-header">
                <h2>
                    Settings for Zone '{zoneName}'
                    <button
                        className="rename-button"
                        onClick={() => setIsRenaming(true)}
                        title="Renaming Zone"
                    >
                        📝
                    </button>
                </h2>
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
                    <button onClick={() => {onRename(newName); setIsRenaming(false); }}>
                        Save Name
                    </button>
                    <button onClick={() => setIsRenaming(false)}>Cancel</button>
                </div>
            )}

            <div className="settings-body">
                <button className="save-btn" onClick={onSave}>Save</button>
                <button className="delete-btn" onClick={onDelete}>Delete</button>
            </div>
        </div>
    );
};

export default ZoneSettings;