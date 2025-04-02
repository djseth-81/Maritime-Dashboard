import { ImageryLayer, WebMapServiceImageryProvider } from "cesium";
import { useCesium } from "resium";
import { useEffect, useState } from "react";


/* 
    Explore weather APIs,
    and figure out how to add weather data to the globe
    Ideally it would be in Cesium Geometries, with color for severity of weather
    red for severe, yellow for moderate, green for mild
    and the weather data would be updated in real time. 
    The specific information about a storm or weather event would be displayed in a popup
    when the user clicks on the weather data. 
    It would provide wind speed, direction, and other relevant information.
    Ocean conditions should also be included, such as wave height and direction.

*/
const WeatherOverlay = ({ showWeather }) => {


    useEffect(() => {

    }, []);

    return null;
};

export default WeatherOverlay