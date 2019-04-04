import * as GJV from "geojson-validation";
import {GeoData, GeographicInfo, ModuleType, PointGeoInfo, RdnsType} from "../reducers/map-reducer";
import {uuidv4} from "../utilities";
import countries from "./countries.json";

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
        rdnsType?: RdnsType;
        rdnsCircleInfo?: {
            circleRadius: number;
            circleUnit: string;
        };
        rdnsLabel?: string;
        rdnsTextInfo?: string;
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

const convertToGeometry: (geoInfo: GeographicInfo) => GeometryMultiPolygon | GeometryPoint = (geoInfo) => {
    switch (geoInfo.geoData.type) {
        case ModuleType.MultiPolygon:
            return {
                type: "MultiPolygon",
                coordinates: [geoInfo.geoData.points.map((polygon) => {
                    const multiPolygon = polygon.map((point) => [point.lng, point.lat]);
                    if (multiPolygon.length > 0) {
                        multiPolygon.push(multiPolygon[0]);
                    }
                    return multiPolygon;
                })],
            };
        case ModuleType.Point:
            const geoData = geoInfo.geoData as PointGeoInfo;
            return {
                type: "Point",
                coordinates: geoData.center
                    ? [geoData.center.lng, geoData.center.lat]
                    : [],
            };
    }
};

export const saveToGeoJson: (geoInfos: { [uuid: string]: GeographicInfo }) => GEOJson = (geoInfos) =>
    ({
        type: "FeatureCollection",
        features: Object.values(geoInfos)
            .map((geoInfo) => ({
                type: "Feature",
                geometry: convertToGeometry(geoInfo),
                properties: {
                    rdnsType: geoInfo.rdnsType,
                    rdnsCircleInfo: (geoInfo.geoData.type === ModuleType.Point)
                        ? {circleRadius: geoInfo.geoData.radius, circleUnit: "meters"}
                        : undefined,
                    rdnsLabel: geoInfo.label,
                    rdnsTextInfo: geoInfo.textInfo,
                },
            })),
    });

export const toGeoData: (feature: GEOJsonFeature) => GeoData = (feature) => {
    switch (feature.properties.rdnsType) {
        case RdnsType.Channel:
        case RdnsType.Headquarters:
            return {
                type: ModuleType.Point,
                radius: feature.properties.rdnsCircleInfo ? feature.properties.rdnsCircleInfo.circleRadius : 0,
                center: {
                    lat: (feature.geometry as GeometryPoint).coordinates[1],
                    lng: (feature.geometry as GeometryPoint).coordinates[0],
                },
            };
        default:
            return {
                type: ModuleType.MultiPolygon,
                points: (feature.geometry as GeometryMultiPolygon).coordinates
                    .flatMap((superMultiPolygon) => {
                        return superMultiPolygon
                                .map((multiPolygon) => multiPolygon
                                    .map((polygon) => ({lat: polygon[1], lng: polygon[0]})),
                                )
                        },
                    ),
            }
    }
};

export const importFromGeoJson: (geoJson: GEOJson) => GeoJSONParsedResult
    = (geoJson) => {
    const warnings: string[] = [];

    if (!GJV.valid(geoJson)) {
        return {errors: "Invalid GeoJSON format!"};
    }

    if (geoJson.type !== "FeatureCollection") {
        return {errors: "The rdnsType the root element of the GeoJSON must be \"FeatureCollection\""};
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

            if (properties.rdnsType === RdnsType.Channel && !properties.rdnsCircleInfo) {
                warnings
                    .push(`An rdns Channel entry must have a \"rdnsCircleInfo\" property in its properties. This entry will be ignored: ${feature}`);
                return false;
            }
            return true;
        })
        .forEach((feature) => {
            const uuid: string = uuidv4();
            geographicInfos = {
                ...geographicInfos, [uuid]: {
                    id: uuid,
                    rdnsType: feature.properties.rdnsType!,
                    geoData: toGeoData(feature),
                    label: feature.properties.rdnsLabel || "",
                    textInfo: feature.properties.rdnsTextInfo || "",
                    injected: true,
                },
            }
        });

    return {
        geographicInfos,
        warnings,
    }
};
