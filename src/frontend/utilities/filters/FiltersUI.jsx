import { useState, useEffect } from 'react';
import useFetchFilters from './Filters';

/**
 * FiltersUI component to display and manage filter options for vessels.
 * @param {Object} props - Component props.
 * @param {string} props.apiEndpoint - API endpoint to fetch filter options.
 * @param {Function} props.onFilterApply - Callback function to apply selected filters.
 * @returns {JSX.Element} - Rendered component.
 * @description This component fetches filter options from the API and allows users to select filters for vessel tracking.
 */

const FiltersUI = ({ apiEndpoint, onFilterApply }) => {
    const {
        filterOptions,
        selectedFilters,
        setSelectedFilters,
        loading,
        error
    } = useFetchFilters(apiEndpoint);

    const vesselTypes = [
        "CARGO",
        "FISHING",
        "TANKER",
        "TUG",
        "PASSENGER",
        "RECREATIONAL",
        "OTHER",
    ]

    const [orderedVesselTypes, setOrderedVesselTypes] = useState(vesselTypes);

    useEffect(() => {
        if (filterOptions?.types) {
            const orderedTypes = vesselTypes.filter(type => filterOptions.types.includes(type));
            const extraTypes = filterOptions.types.filter(type => !vesselTypes.includes(type)); // catch any extra types
            setOrderedVesselTypes([...orderedTypes, ...extraTypes]);
            setSelectedFilters((prev) => ({
                ...prev,
                types: filterOptions.types
            }));
        }
    }, [filterOptions]);

    const handleTypeChange = (event) => {
        const { value, checked } = event.target;

        const updatedFilters = checked
            ? [...selectedFilters.types, value]
            : selectedFilters.types.filter((type) => type !== value);

        setSelectedFilters((prev) => ({
            ...prev,
            types: updatedFilters
        }));

        onFilterApply({
            ...selectedFilters,
            types: updatedFilters
        });
    };

    const handleOriginChange = (event) => {
        const { value } = event.target;
        setSelectedFilters((prev) => ({
            ...prev,
            origin: value
        }));
    };

    const handleStatusChange = (event) => {
        const { value, checked } = event.target;
        const updatedStatuses = checked
            ? [...selectedFilters.statuses, value]
            : selectedFilters.statuses.filter((status) => status !== value);

        setSelectedFilters((prev) => ({
            ...prev,
            statuses: updatedStatuses
        }));

        onFilterApply({
            ...selectedFilters,
            statuses: updatedStatuses
        });
    };

    const handleApplyFilters = () => {
        const typesToSend = selectedFilters.types.length ? selectedFilters.types : ["NONE"];

        onFilterApply({
            ...selectedFilters,
            types: typesToSend
        });
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="filter-subwindow">
            <div className='vessel-subwindow'>
                <label>Vessel Type:</label>
                {orderedVesselTypes.map((type) => (
                    <label key={type}>
                        <input
                            type="checkbox"
                            value={type}
                            checked={selectedFilters.types.includes(type)}
                            onChange={handleTypeChange}
                        />
                        {type}
                    </label>
                ))}
            </div>

            <div className='origin-subwindow'>
                <label>Country of Origin:</label>
                <input
                    type="text"
                    value={selectedFilters.origin}
                    onChange={handleOriginChange}
                    placeholder="Enter country of origin"
                />
            </div>

            <div className='status-subwindow'>
                <label>Status:</label>
                {filterOptions?.current_status?.map((status) => (
                    <label key={status}>
                        <input
                            type="checkbox"
                            value={status}
                            checked={selectedFilters.statuses.includes(status)}
                            onChange={handleStatusChange}
                        />
                        {status}
                    </label>
                ))}
            </div>

            <button onClick={handleApplyFilters}>Apply Filters</button>
        </div>
    );
};

export default FiltersUI;
