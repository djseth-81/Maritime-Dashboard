import { useState } from 'react';

const FiltersUI = ({ showVesselTypes, showOrigin, showStatus, onClose }) => {
    const [countryOfOrigin, setCountryOfOrigin] = useState('');

    // Implementation of checkbox change handler, requires DB implementation to be fully functional.
    const handleVesselCheckboxChange = (event) => {
        const { name, checked } = event.target;
    };

    // Implementation of country of origin change handler, requires DB implementation to be fully functional.
    const handleCountryChange = (event) => {
        setCountryOfOrigin(event.target.value);
    }

    // Implementation of status checkbox change handler, requires DB implementation to be fully functional.
    const handleStatusCheckboxChange = (event) => {
        const { name, checked } = event.target;
    }

    return (

        <div className="filter-subwindow">

            {showVesselTypes && (
                <div className='vessel-subwindow'>
                    <label>
                        <input type="checkbox" name="all" onChange={handleVesselCheckboxChange} />
                        Select/Deselect All
                    </label>
                    <label>
                        <input type="checkbox" name="tanker" onChange={handleVesselCheckboxChange} />
                        Tanker
                    </label>
                    <label>
                        <input type="checkbox" name="cargo" onChange={handleVesselCheckboxChange} />
                        Cargo
                    </label>
                    <label>
                        <input type="checkbox" name="fishing" onChange={handleVesselCheckboxChange} />
                        Fishing
                    </label>
                    <label>
                        <input type="checkbox" name="leasure" onChange={handleVesselCheckboxChange} />
                        Leasure
                    </label>
                    <label>
                        <input type="checkbox" name="other" onChange={handleVesselCheckboxChange} />
                        Other
                    </label>
                    {/* Add more vessel types, should align with DB values */}

                </div>
            )}

            {showOrigin && (
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

            {showStatus && (
                <div className='status-subwindow'>
                    <label>
                        <input type="checkbox" name="docked" onChange={handleStatusCheckboxChange} />
                        Docked
                    </label>
                    <label>
                        <input type="checkbox" name="underway" onChange={handleStatusCheckboxChange} />
                        Underway
                    </label>
                    <label>
                        <input type="checkbox" name="unknown" onChange={handleStatusCheckboxChange} />
                        Unknown
                    </label>
                    {/* Add more statuses */}
                </div>
            )}
        </div>
    );
};

export default FiltersUI