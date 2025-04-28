import React, { useState } from "react";
import { Viewer, ImageryLayer } from "resium";
import * as Cesium from "cesium";

const layerOptions = {
  Clouds: "clouds_new",
  Precipitation: "precipitation_new",
  Wind: "wind_new",
  Temperature: "temp_new",
};

const legendMap = {
  clouds_new: "https://tile.openweathermap.org/map/clouds_new/legend.png",
  precipitation_new: "https://tile.openweathermap.org/map/precipitation_new/legend.png",
  wind_new: "https://tile.openweathermap.org/map/wind_new/legend.png",
  temp_new: "https://tile.openweathermap.org/map/temp_new/legend.png",
};

function WeatherRadar() {
  const [showRadar, setShowRadar] = useState(false);
  const [selectedLayer, setSelectedLayer] = useState("clouds_new");

  const imageryProvider = new Cesium.UrlTemplateImageryProvider({
    url: `https://tile.openweathermap.org/map/${selectedLayer}/{z}/{x}/{y}.png?appid=YOUR_API_KEY`,
    credit: `Weather data © OpenWeatherMap - ${selectedLayer}`,
  });

  return (
    <div className="weather-radar">
      <div className="">
        <label htmlFor="layer-select" className="mr-2">Layer:</label>
        <select
          id="layer-select"
          value={selectedLayer}
          onChange={(e) => setSelectedLayer(e.target.value)}
        >
          {Object.entries(layerOptions).map(([name, value]) => (
            <option key={value} value={value}>{name}</option>
          ))}
        </select>
      </div>

      <button
        className=""
        onClick={() => setShowRadar((prev) => !prev)}
      >
        {showRadar ? "Hide Weather" : "Show Weather"}
      </button>

      <Viewer full>
        {showRadar && <ImageryLayer imageryProvider={imageryProvider} />}
      </Viewer>

      {/* Legend for weather tools */}
      {showRadar && (
        <div className="">
          <img
            src={legendMap[selectedLayer]}
            alt="Legend"
            className="max-w-xs"
          />
        </div>
      )}
    </div>
  );
}

export default WeatherRadar;
