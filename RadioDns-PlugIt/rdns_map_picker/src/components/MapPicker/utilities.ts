// https://groups.google.com/forum/#!topic/google-maps-js-api-v3/hDRO4oHVSeM
export const getMetersPerPixel: (map: google.maps.Map, lat: number) => number
    = (map, lat) => 156543.03392 * Math.cos(lat * Math.PI / 180) / Math.pow(2, map.getZoom());
