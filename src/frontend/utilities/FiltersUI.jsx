import { useState } from 'react';

const FiltersUI = ({ showVesselTypes, showOrigin, showStatus, onClose }) => {
    const [countryOfOrigin, setCountryOfOrigin] = useState('');

    // Implementation of checkbox change handler, requires DB implementation to be fully functional.
    const handleCheckboxChange = (event) => {
        const { name, checked } = event.target;
    };

    // Implementation of country of origin change handler, requires DB implementation to be fully functional.
    const handleCountryChange = (event) => {
        setCountryOfOrigin(event.target.value);
    }

    return (

        <div className="filter-subwindow">

            {showVesselTypes && (
                <div className='vessel-subwindow'>
                    <label>
                        <input type="checkbox" name="all" onChange={handleCheckboxChange} />
                        Select/Deselect All
                    </label>
                    <label>
                        <input type="checkbox" name="tanker" onChange={handleCheckboxChange} />
                        Tanker
                    </label>
                    <label>
                        <input type="checkbox" name="cargo" onChange={handleCheckboxChange} />
                        Cargo
                    </label>
                    <label>
                        <input type="checkbox" name="fishing" onChange={handleCheckboxChange} />
                        Fishing
                    </label>
                    <label>
                        <input type="checkbox" name="leasure" onChange={handleCheckboxChange} />
                        Leasure
                    </label>
                    <label>
                        <input type="checkbox" name="other" onChange={handleCheckboxChange} />
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
                        <input type="checkbox" name="docked" onChange={handleCheckboxChange} />
                        Docked
                    </label>
                    <label>
                        <input type="checkbox" name="underway" onChange={handleCheckboxChange} />
                        Underway
                    </label>
                    <label>
                        <input type="checkbox" name="unknown" onChange={handleCheckboxChange} />
                        Unknown
                    </label>
                    {/* Add more statuses */}
                </div>
            )}
        </div>
    );
};

export default FiltersUI