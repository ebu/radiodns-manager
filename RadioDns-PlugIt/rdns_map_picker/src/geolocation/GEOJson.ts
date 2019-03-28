import countries from "./countries.json";

export interface GeometryPolygon {
    type: "Polygon";
    coordinates: number[][][];
}

export interface GeometryMultiPolygon {
    type: "MultiPolygon",
    coordinates: number[][][][];
}

export interface GEOJsonFeature {
    type: string;
    geometry: GeometryPolygon | GeometryMultiPolygon;
    properties: {
        ADMIN: string;
        ISO_A3: string;
    }
}

export interface GEOJson {
    type: string;
    features: GEOJsonFeature[];
}

export const getGeoJson: () => Promise<GEOJsonFeature[]> = async () => (countries as GEOJson).features
        .filter((feature) => feature.geometry.type === "Polygon" || feature.geometry.type === "MultiPolygon");
