import { useState } from 'react';
import useFetchFilters from './Filters';

const FiltersUI = ({ apiEndpoint }) => {
    const { vessels, filterOptions, loading, error } = useFetchFilters(apiEndpoint);
    const [countryOfOrigin, setCountryOfOrigin] = useState('');

    const handleVesselCheckboxChange = (event) => {
        const { name, checked } = event.target;
        // Handle vessel checkbox change
    };

    const handleCountryChange = (event) => {
        setCountryOfOrigin(event.target.value);
    };

    const handleStatusCheckboxChange = (event) => {
        const { name, checked } = event.target;
        // Handle status checkbox change
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="filter-subwindow">
            {filterOptions.types.length > 0 && (
                <div className='vessel-subwindow'>
                    <label>
                        <input type="checkbox" name="all" onChange={handleVesselCheckboxChange} />
                        Select/Deselect All
                    </label>
                    {filterOptions.types.map((type) => (
                        <label key={type}>
                            <input type="checkbox" name={type} onChange={handleVesselCheckboxChange} />
                            {type}
                        </label>
                    ))}
                </div>
            )}

            {filterOptions.origins.length > 0 && (
                <div className='origin-subwindow'>
                    <label>
                        <input
                            type="text"
                            value={countryOfOrigin}
                            onChange={handleCountryChange}
                            placeholder='Enter country of origin'
                        />
                    </label>
                </div>
            )}

            {filterOptions.statuses.length > 0 && (
                <div className='status-subwindow'>
                    {filterOptions.statuses.map((status) => (
                        <label key={status}>
                            <input type="checkbox" name={status} onChange={handleStatusCheckboxChange} />
                            {status}
                        </label>
                    ))}
                </div>
            )}
        </div>
    );
};

export default FiltersUI;