// https://groups.google.com/forum/#!topic/google-maps-js-api-v3/hDRO4oHVSeM

import {GeoData, ModuleType} from "../../reducers/map-reducer";
import {PolygonModule} from "../map/google/modules/PolygonModule";

export const getMetersPerPixel: (map: google.maps.Map, lat: number) => number
    = (map, lat) => 156543.03392 * Math.cos(lat * Math.PI / 180) / Math.pow(2, map.getZoom());

export const getCenterOfGeoData = (geoData: GeoData, defaultPos: google.maps.LatLngLiteral) => {
    let center = defaultPos;
    switch (geoData.type) {
        case ModuleType.MultiPolygon:
            center = PolygonModule.returnCenter(geoData.points);
            break;
        case ModuleType.Point:
            if (geoData.center) {
                center = geoData.center;
            }
            break;
    }
    return center;
};
