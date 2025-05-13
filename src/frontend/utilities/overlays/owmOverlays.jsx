import axios from "axios";
import { convertCartesianToDegrees } from "../coordUtils";
import { toast } from "react-toastify";

 export const retrieveOverlays = async (weatherLayers, setWeatherLayers) => {
    const url = "http:" + URL[1] + ":8000/weather/";

    if (!weatherLayers) {
        try {
            const response = await axios.get(url);
            if (response.data.length === 0) {
                console.log("No available weather overlays.");
                return;
            }

            // const layerOptions = {
            //     Clouds: cloudLayer,
            //     Precipitation: precipitationLayer,
            //     Wind: windLayer,
            //     Temperature: temperatureLayer,
            //     "US Precipitation": radarLayer
            // };
            // setWeatherLayers(layerOptions)
            console.log("Overlays report");
            console.log(response.data.payload);

        } catch (error) {
            console.error("Error fetching weather overlays:", error.message);
            toast.error("Failed loading overlays.");
            setWeatherLayers(null);
        }
    }
};
