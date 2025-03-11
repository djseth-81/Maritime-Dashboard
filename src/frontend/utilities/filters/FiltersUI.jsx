import { useState } from 'react';
import useFetchFilters from './Filters';

const FiltersUI = ({ apiEndpoint, onFilterApply }) => {
    const { filterOptions, loading, error } = useFetchFilters(apiEndpoint);
    const [selectedFilters, setSelectedFilters] = useState({
        types: [],
        origin: "",
        statuses: []
    });

    const handleTypeChange = (event) => {
        const { value, checked } = event.target;
        setSelectedFilters((prev) => ({
            ...prev,
            types: checked
                ? [...prev.types, value]
                : prev.types.filter((type) => type !== value)
        }));
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
        setSelectedFilters((prev) => ({
            ...prev,
            statuses: checked
                ? [...prev.statuses, value]
                : prev.statuses.filter((status) => status !== value)
        }));
    };

    // const handleFilterChange = (event) => {
    //     const { name, value } = event.target;
    //     setSelectedFilters((prev) => ({
    //         ...prev,
    //         [name]: value
    //     }));
    // };

    const handleApplyFilters = () => {
        onFilterApply(selectedFilters);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="filter-subwindow">
            <div className='vessel-subwindow'>
                <label>Vessel Type:</label>
                {filterOptions?.types?.map((type) => (
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
                {filterOptions?.statuses?.map((status) => (
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
