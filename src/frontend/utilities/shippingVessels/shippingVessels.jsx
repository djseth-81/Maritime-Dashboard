import React, { useMemo, useState, useCallback, useEffect } from 'react'
import { Entity } from 'resium'
import { Cartesian3, DistanceDisplayCondition, NearFarScalar, Color } from 'cesium'
import BoatIcon from "../../assets/icons/boatIcon"


const position = useMemo(() => {
  if (isNaN(numLongitude) || isNaN(numLatitude) || isNaN(numElevation)) {
    console.warn(`Invalid coordinates for satellite ${name}:`, { longitude, latitude, elevation })
    return Cartesian3.fromDegrees(0, 0, 0)
  }
  return Cartesian3.fromDegrees(numLongitude, numLatitude, numElevation)
}, [numLongitude, numLatitude, numElevation, name])