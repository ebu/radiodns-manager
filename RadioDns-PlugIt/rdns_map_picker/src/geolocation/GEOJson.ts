import countries from "./countries.json";
import {GeographicInfo} from "../reducers/map-reducer";
import {MapPickerModuleType} from "../components/MapPicker/modules/MapPickerModule";
import {MarkerModule} from "../components/MapPicker/modules/MarkerModule";
import * as GJV from "geojson-validation";
import {PolygonModule} from "../components/MapPicker/modules/PolygonModule";
import {uuidv4} from "../utilities";

export interface GeometryPolygon {
    type: "Polygon";
    coordinates: number[][][];
}

export interface GeometryMultiPolygon {
    type: "MultiPolygon",
    coordinates: number[][][][];
}

export interface GeometryPoint {
    type: "Point",
    coordinates: number[],
}

export type Geometry = GeometryPolygon | GeometryMultiPolygon | GeometryPoint;

export interface GEOJsonFeature {
    type: string;
    geometry: Geometry;
    properties: {
        ADMIN?: string;
        ISO_A3?: string;
        rdnsType?: MapPickerModuleType;
        rdnsCircleInfo?: {
            circleRadius: number;
            circleUnit: string;
        }
    }
}

export interface GeoJSONParsedResult {
    geographicInfos?: { [uuid: string]: GeographicInfo };
    error?: string;
    warnings?: string[];
}

export interface GEOJson {
    type: string;
    features: GEOJsonFeature[];
}

export const getGeoJson: () => Promise<GEOJsonFeature[]> = async () => (countries as GEOJson).features
    .filter((feature) => feature.geometry.type === "Polygon" || feature.geometry.type === "MultiPolygon");


const convertToGeometry: (type: MapPickerModuleType, points: google.maps.LatLngLiteral[][]) => GeometryMultiPolygon | GeometryPoint =
    (type, points) => {
        switch (type) {
            case MapPickerModuleType.Station:
            case MapPickerModuleType.Country:
                return {
                    type: "MultiPolygon",
                    coordinates: [points.map((polygon) => {
                        const multiPolygon = polygon.map((point) => [point.lng, point.lat]);
                        if (multiPolygon.length > 0) {
                            multiPolygon.push(multiPolygon[0]);
                        }
                        return multiPolygon;
                    })]
                };
            case MapPickerModuleType.Channel:
            case MapPickerModuleType.Headquarters:
                return {
                    type: "Point",
                    coordinates: points[0].flatMap((point) => [point.lng, point.lat]),
                };
        }
    };

export const saveToGeoJson: (geoInfos: { [uuid: string]: GeographicInfo }) => GEOJson = (geoInfos) =>
    ({
        type: "FeatureCollection",
        features: Object.values(geoInfos)
            .map((geoInfo) => ({
                type: "Feature",
                geometry: convertToGeometry(geoInfo.type, geoInfo.module.returnPoints()),
                properties: {
                    rdnsType: geoInfo.type,
                    rdnsCircleInfo: geoInfo.type === MapPickerModuleType.Channel
                        ? {circleRadius: (geoInfo.module as MarkerModule).getCircleRadius(), circleUnit: "meters"}
                        : undefined,
                }
            })),
    });

const toMapPickerModule = (
    uuid: string,
    feature: GEOJsonFeature,
    map: google.maps.Map,
    setActive: (uuid: string) => () => void,
    openDeleteMenu: () => void
) => {
    switch (feature.properties.rdnsType!) {
        case MapPickerModuleType.Country:
        case MapPickerModuleType.Station:
            const paths = (feature.geometry as GeometryMultiPolygon).coordinates
                .flatMap((superMultiPolygon) => superMultiPolygon
                    .map((multiPolygon) => multiPolygon
                        .map((polygon) => ({lat: polygon[1], lng: polygon[0]}))
                    )
                );
            return new PolygonModule({
                map,
                editable: MapPickerModuleType.Station === feature.properties.rdnsType!,
                draggable: MapPickerModuleType.Station === feature.properties.rdnsType!,
                noClick: true,
                setActive: setActive(uuid),
                openDeleteMenu,
                paths,
            }).init();
        case MapPickerModuleType.Headquarters:
        case MapPickerModuleType.Channel:
            return new MarkerModule({
                map,
                editable: true,
                draggable: true,
                noClick: true,
                setActive: setActive(uuid),
                openDeleteMenu,
                position: {
                    lat: (feature.geometry as GeometryPoint).coordinates[1],
                    lng: (feature.geometry as GeometryPoint).coordinates[0]
                },
                circleRadius: feature.properties.rdnsType! === MapPickerModuleType.Channel
                    ? feature.properties.rdnsCircleInfo!.circleRadius
                    : undefined,
            }).init()
    }
};

export const importFromGeoJson: (
    geoJson: GEOJson,
    map: google.maps.Map,
    setActive: (uuid: string) => () => void,
    openDeleteMenu: () => void
) => GeoJSONParsedResult
    = (geoJson, map, setActive, openDeleteMenu) => {
    const warnings: string[] = [];

    if (!GJV.valid(geoJson)) {
        return {errors: "Invalid GeoJSON format!"};
    }

    if (geoJson.type !== "FeatureCollection") {
        return {errors: "The type the root element of the GeoJSON must be \"FeatureCollection\""};
    }

    let geographicInfos: { [uuid: string]: GeographicInfo } = {};
    geoJson.features
        .filter((feature) => {
            const {properties} = feature;

            if (!properties) {
                warnings.push(`A feature must have an \"properties\" property. This entry will be ignored: ${feature}`);
                return false;
            }

            if (!properties.rdnsType) {
                warnings.push(`A feature must have an \"rdnsType\" property in its properties. This entry will be ignored: ${feature}`);
                return false;
            }

            if (properties.rdnsType === MapPickerModuleType.Channel && !properties.rdnsCircleInfo) {
                warnings.push(`An rdns Channel entry must have a \"rdnsCircleInfo\" property in its properties. This entry will be ignored: ${feature}`);
                return false;
            }
            return true;
        })
        .forEach((feature) => {
            const uuid = uuidv4();
            geographicInfos = {
                ...geographicInfos, [uuid]: {
                    id: uuid,
                    type: feature.properties.rdnsType!,
                    module: toMapPickerModule(
                        uuid,
                        feature,
                        map,
                        setActive,
                        openDeleteMenu,
                    ),
                }
            }
        });

    return {
        geographicInfos,
        warnings,
    }
};

