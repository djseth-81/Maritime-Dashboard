/* 

This is Sean's attempt at API fetching for filtering types.
Remove or replace this file with the actual API fetching code if found necessary.

*/

import { useEffect, useState } from 'react';
import axios from 'axios';

const useFetchFilters = (apiEndpoint) => {
    const [vessels, setVessels] = useState([]);
    const [filterOptions, setFilterOptions] = useState({
        types: [],
        origins: [],
        statuses: []
    });
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const source = axios.CancelToken.source();
        setLoading(true);
        axios.get(apiEndpoint, { cancelToken: source.token })
            .then((response) => {
                const data = response.data;
                setVessels(data);

                const types = [...new Set(data.map(vessel => vessel.type))];
                const origins = [...new Set(data.map(vessel => vessel.origin))];
                const statuses = [...new Set(data.map(vessel => vessel.status))];
                setFilterOptions({ types, origins, statuses });
                
            })
            .catch((error) => {
                if (axios.isCancel(error)) {
                    console.log('Request canceled', error.message);
                } else {
                    setError(`Error fetching vessel data: ${error.message}`);
                }
            })
            .finally(() => {
                setLoading(false);
            });

        return () => {
            source.cancel('Operation canceled by the user.');
        };
    }, [apiEndpoint]);

    return { vessels, filterOptions, loading, error };
};

export default useFetchFilters;