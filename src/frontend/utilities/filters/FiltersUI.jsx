import { useState } from 'react';
import useFetchFilters from './Filters';

const FiltersUI = ({ apiEndpoint, onFilterApply }) => {
    const { filterOptions, loading, error } = useFetchFilters(apiEndpoint);
    const [selectedFilters, setSelectedFilters] = useState({
        type: "",
        origin: "",
        status: ""
    });

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        setSelectedFilters((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    const handleApplyFilters = () => {
        onFilterApply(selectedFilters);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="filter-subwindow">
            <div className='vessel-subwindow'>
                <label>Vessel Type:</label>
                <select name="type" onChange={handleFilterChange}>
                    <option value="">All</option>
                    {filterOptions.types.map((type) => (
                        <option key={type} value={type}>{type}</option>
                    ))}
                </select>
            </div>

            <div className='origin-subwindow'>
                <label>Country of Origin:</label>
                <select name="origin" onChange={handleFilterChange}>
                    <option value="">All</option>
                    {filterOptions.origins.map((origin) => (
                        <option key={origin} value={origin}>{origin}</option>
                    ))}
                </select>
            </div>

            <div className='status-subwindow'>
                <label>Status:</label>
                <select name="status" onChange={handleFilterChange}>
                    <option value="">All</option>
                    {filterOptions.statuses.map((status) => (
                        <option key={status} value={status}>{status}</option>
                    ))}
                </select>
            </div>

            <button onClick={handleApplyFilters}>Apply Filters</button>
        </div>
    );
};

export default FiltersUI;
