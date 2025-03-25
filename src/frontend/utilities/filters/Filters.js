import { useEffect, useState } from 'react';
import axios from 'axios';

const useFetchFilters = (apiEndpoint) => {
    const [filterOptions, setFilterOptions] = useState({
        types: [],
        origins: [],
        statuses: []
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isMounted = true; 
        setLoading(true);

        axios.get(apiEndpoint)
            .then((response) => {
                if (isMounted) {
                    const data = response.data;
                    setFilterOptions(data);
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

        return () => {
            isMounted = false;
        };
    }, [apiEndpoint]);

    return { filterOptions, loading, error };
};

export default useFetchFilters;
