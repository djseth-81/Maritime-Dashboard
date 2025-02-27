
const Filters = ({ onClose }) => {

    return (
        // placeholder values and buttons
        <div className="filter-panel">
            <h3>Filters</h3>
            <button onClick={onClose}>Close</button>
            <button>Vessel Type</button>
            <button> Country of Origin </button>
            <button> Status </button>
        </div>
    );
};

export default Filters