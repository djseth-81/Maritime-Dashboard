import { ImageryLayer, WebMapServiceImageryProvider } from "cesium";
import { useCesium } from "resium";
import { useEffect, useState } from "react";
import * as Cesium from 'cesium'

const WeatherOverlay = ({ onActiveWeatherLayer }) => {
    const [showWeatherMenu, setShowWeatherMenu] = useState(true);
    const weatherOverlayOptions = ["Clouds", "Precipitation", "Wind", "Temperature", "US Precipitation"]

    return (
    <div>
      <div class="menu-header">
        Layers
      </div>
  
        {showWeatherMenu && (
          <div>
            {weatherOverlayOptions.map((layerName) => (
              <button
                key={layerName}
                onClick={() => onActiveWeatherLayer(layerName)}
                style={{width: '100%', marginBottom: "10px"}}
              >
                {layerName}
              </button>
            ))}
            <button style={{width: '100%'}} onClick={() => onActiveWeatherLayer(null)}>Clear Layer</button>
          </div>
        )}
      </div>
    );
};

export default WeatherOverlay