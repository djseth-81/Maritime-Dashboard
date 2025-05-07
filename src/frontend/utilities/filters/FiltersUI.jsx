import { useState, useEffect } from 'react';
import useFetchFilters from './Filters';
import BoatIcon from "../../assets/icons/boatIcon";

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
    loading,
    error,
  } = useFetchFilters(apiEndpoint);

    const vesselTypes = [
        'BUNKER',
        'CARGO',
        'GEAR',
        'TANKER',
        'OTHER',
        'PASSENGER',
        'RECREATIONAL',
        'SEISMIC_VESSEL',
        'TUG',
        'FISHING'];
    const statusTypes = [
        'FISHING',
        'UNMANNED',
        'HAZARDOUS CARGO',
        'IN TOW',
        'ANCHORED',
        'TOWED',
        'LIMITED MOVEMENT',
        'UNDERWAY',
        'UNKNOWN',
        'MOORED'];

  // Temporary state for filters
  const [tempFilters, setTempFilters] = useState({
    types: [],
    origin: "",
    statuses: [],
  });

  useEffect(() => {
    if (filterOptions?.types) {
      setTempFilters((prev) => ({
        ...prev,
        types: filterOptions.types,
      }));
    }

    if (filterOptions?.current_status) {
      setTempFilters((prev) => ({
        ...prev,
        statuses: filterOptions.current_status,
      }));
    }
  }, [filterOptions]);

  const handleTypeChange = (event) => {
    const { value, checked } = event.target;

    const updatedTypes = checked
      ? [...tempFilters.types, value]
      : tempFilters.types.filter((type) => type !== value);

    setTempFilters((prev) => ({
      ...prev,
      types: updatedTypes,
    }));
  };

  const handleStatusChange = (event) => {
    const { value, checked } = event.target;

    const updatedStatuses = checked
      ? [...tempFilters.statuses, value]
      : tempFilters.statuses.filter((status) => status !== value);

    setTempFilters((prev) => ({
      ...prev,
      statuses: updatedStatuses,
    }));
  };

  const handleOriginChange = (event) => {
    const { value } = event.target;
    setTempFilters((prev) => ({
      ...prev,
      origin: value,
    }));
  };

  const handleApplyFilters = () => {
    onFilterApply(tempFilters); // Apply the filters when the button is clicked
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="filter-subwindow">
      <div className="vessel-subwindow">
        <label>Vessel Type:</label>
        {vesselTypes.map((type) => (
          <label key={type} className='vessel-type-label'>
            <BoatIcon className="vessel-icon" type={type} size={20} heading={90}/>
            <input
              type="checkbox"
              value={type}
              checked={tempFilters.types.includes(type)}
              onChange={handleTypeChange}
            />
            {type}
          </label>
        ))}
      </div>

      <div className="origin-subwindow">
        <label>Country of Origin:</label>
        <input
          type="text"
          value={tempFilters.origin}
          onChange={handleOriginChange}
          placeholder="Enter country of origin"
        />
      </div>

      <div className="status-subwindow">
        <label>Status:</label>
        {statusTypes.map((status) => (
          <label key={status}>
            <input
              type="checkbox"
              value={status}
              checked={tempFilters.statuses.includes(status)}
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
