import axios from 'axios';

// TODO: Integrate with App.jsx and utilities/Filters.js

axios.get(apiEndpoint)
    .then((response) => {
        if (isMounted) {
            const data = response.data;
            setFilterOptions(data);

            setSelectedFilters({
                ...selectedFilters,
                types: data.types,
                statuses: data.current_status
            });
        }
    })
    .catch((error) => {
        if (isMounted) {
            setError(`Error fetching vessel data: ${error.message}`);
        }
    })
    .finally(() => {
        if (isMounted) setLoading(false);
    });
