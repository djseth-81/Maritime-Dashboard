import * as Cesium from 'cesium';

/**
 * Converts a Cartesian3 coordinate to degrees (latitude, longitude).
 * @param {Cesium.Cartesian3} cartesian - The Cartesian3 coordinate to convert.
 * @returns {Object} An object containing latitude, longitude, and height.
 */

export const convertCartesianToDegrees = (cartesian) => {
    if (!cartesian) {
        console.warn("Invalid Cartesian coordinate:", cartesian);
        return { latitude: 0, longitude: 0 };
    }

    const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
    const latitude = Cesium.Math.toDegrees(cartographic.latitude);
    const longitude = Cesium.Math.toDegrees(cartographic.longitude);

    return { latitude, longitude };
};