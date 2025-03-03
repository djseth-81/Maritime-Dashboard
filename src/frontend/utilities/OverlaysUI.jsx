
const Overlays = ({ onClose }) => {

    return (
        // placeholder values and buttons
        <div className="overlay-panel">
            <h3>Overlays</h3>
            <button onClick={onClose}>Close</button>
            <button> weather </button>
            <button> Ocean Conditions </button>
            <button> Traffic Heatmaps</button>
        </div>
    );
};

export default Overlays