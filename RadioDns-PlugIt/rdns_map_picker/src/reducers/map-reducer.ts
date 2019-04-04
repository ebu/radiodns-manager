import {Action} from "redux";
import {GEOJsonFeature} from "../geolocation/GEOJson";
import {objectWithoutProperties} from "../utilities";

// Types
const SET_MAP_PROVIDER = "radiodns-manager/map/SET_MAP_PROVIDER";
const SET_CURRENTLY_EDITED = "radiodns-manager/map/SET_CURRENTLY_EDITED";
const ADD_GEOINFO = "radiodns-manager/map/ADD_GEOINFO";
const UPDATE_GEOINFO_MULTIPOLYGON = "radiodns-manager/map/UPDATE_GEOINFO_MULTIPOLYGON";
const UPDATE_GEOINFO_POINT = "radiodns-manager/map/UPDATE_GEOINFO_POINT";
const ADD_GEOINFO_BULK = "radiodns-manager/map/ADD_GEOINFO_BULK";
const DELETE_GEOINFO = "radiodns-manager/map/DELETE_GEOINFO";
const SET_GEOJSON = "radiodns-manager/map/SET_GEOJSON";
const SET_GOOGLE_MAP = "radiodns-manager/map/SET_GOOGLE_MAP";

interface SetMapProviderAction extends Action<typeof SET_MAP_PROVIDER> {
    mapProvider: MapProvider;
}

interface AddGeoInfosAction extends Action<typeof ADD_GEOINFO> {
    uuid: string;
    geoInfo: GeographicInfo;
}

interface UpdateGeoInfosMultipolygonAction extends Action<typeof UPDATE_GEOINFO_MULTIPOLYGON> {
    uuid: string;
    points: google.maps.LatLngLiteral[][];
}

interface UpdateGeoInfosPointAction extends Action<typeof UPDATE_GEOINFO_POINT> {
    uuid: string;
    center: google.maps.LatLngLiteral;
    radius: number;
}

interface AddGeoInfosBulkAction extends Action<typeof ADD_GEOINFO_BULK> {
    geoInfos: { [uuid: string]: GeographicInfo }
}

interface DeleteGeoInfosAction extends Action<typeof DELETE_GEOINFO> {
    uuid: keyof MapReducerState;
}

interface SetCurrentlyEditedAction extends Action<typeof SET_CURRENTLY_EDITED> {
    currentlyEditedUuid: keyof MapReducerState;
}

interface SetGEOJSONAction extends Action<typeof SET_GEOJSON> {
    geoJson: GeoJsonData;
}

interface SetGoogleMapAction extends Action<typeof SET_GOOGLE_MAP> {
    map: google.maps.Map;
}

type MapActions =
    | SetMapProviderAction
    | SetGoogleMapAction
    | SetGEOJSONAction
    | DeleteGeoInfosAction
    | SetCurrentlyEditedAction
    | AddGeoInfosAction
    | UpdateGeoInfosMultipolygonAction
    | UpdateGeoInfosPointAction
    | AddGeoInfosBulkAction;

export enum RdnsType {
    Headquarters = "Headquarters",
    Station = "Station",
    Channel = "Channel",
    Country = "Country",
}

export enum ModuleType {
    MultiPolygon,
    Point,
}

export interface GeographicInfo {
    id: string;
    rdnsType: RdnsType;
    geoData: GeoData;
    label: string;
    textInfo: string;
    injected: boolean;
}

export interface PolygonGeoInfo {
    type: ModuleType.MultiPolygon;
    points: google.maps.LatLngLiteral[][];
}

export interface PointGeoInfo {
    type: ModuleType.Point;
    center?: google.maps.LatLngLiteral;
    radius: number;
}

export type GeoData = PolygonGeoInfo | PointGeoInfo;

export interface GeoJsonData {
    polygons: GEOJsonFeature[];
    status: "LOADING" | "FAILED" | "COMPLETED";
}

export enum MapProvider {
    Google,
    OpenStreetMaps,
}

export interface MapReducerState {
    geoInfos: { [uuid: string]: GeographicInfo };
    currentlyEditedUuid: string;
    geoJson: GeoJsonData;
    mapProvider: MapProvider;
    map: google.maps.Map | null;
}

// Reducer
export const MAP_REDUCER_DEFAULT_STATE: MapReducerState = {
    geoInfos: {},
    currentlyEditedUuid: "",
    geoJson: {
        polygons: [],
        status: "LOADING",
    },
    mapProvider: MapProvider.Google,
    map: null,
};

export function reducer(state: MapReducerState = MAP_REDUCER_DEFAULT_STATE, action: MapActions): MapReducerState {
    switch (action.type) {
        case SET_MAP_PROVIDER:
            return {...state, mapProvider: action.mapProvider};
        case SET_CURRENTLY_EDITED:
            return {...state, currentlyEditedUuid: action.currentlyEditedUuid};
        case ADD_GEOINFO:
            return {
                ...state,
                geoInfos: {...state.geoInfos, [action.uuid]: action.geoInfo},
                currentlyEditedUuid: action.uuid,
            };
        case UPDATE_GEOINFO_MULTIPOLYGON:
            return {
                ...state,
                geoInfos: {...state.geoInfos,
                           [action.uuid]: {
                    ...state.geoInfos[action.uuid],
                    geoData: {
                            ...state.geoInfos[action.uuid].geoData,
                            type: ModuleType.MultiPolygon,
                            points: [...action.points],
                        },
                    },
                },
            };
        case UPDATE_GEOINFO_POINT:
            return {
                ...state,
                geoInfos: {...state.geoInfos,
                           [action.uuid]: {
                        ...state.geoInfos[action.uuid],
                        geoData: {
                            ...state.geoInfos[action.uuid].geoData,
                            type: ModuleType.Point,
                            center: action.center,
                            radius: action.radius,
                        },
                    },
                },
            };
        case ADD_GEOINFO_BULK:
            return {
                ...state,
                geoInfos: {...state.geoInfos, ...action.geoInfos},
            };
        case DELETE_GEOINFO: {
            const newState = {...state};
            newState.geoInfos = objectWithoutProperties(newState.geoInfos, [action.uuid]);
            return newState;
        }
        case SET_GEOJSON:
            return {...state, geoJson: action.geoJson};
        case SET_GOOGLE_MAP:
            return {...state, map: action.map};
        default:
            return state;
    }
}

// Action creators

export const setMapProvider: (mapProvider: MapProvider) => SetMapProviderAction = (mapProvider) => ({
    type: SET_MAP_PROVIDER,
    mapProvider,
});

export const setCurrentlyEdited: (currentlyEditedUuid: string) => SetCurrentlyEditedAction = (currentlyEditedUuid) => ({
    type: SET_CURRENTLY_EDITED,
    currentlyEditedUuid: currentlyEditedUuid as keyof MapReducerState,
});

export const addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => AddGeoInfosAction = (uuid, geoInfo) => ({
    type: ADD_GEOINFO,
    uuid,
    geoInfo,
});

export const updateGeoInfosMultiPolygons: (uuid: string, points: google.maps.LatLngLiteral[][]) => UpdateGeoInfosMultipolygonAction =
    (uuid, points) => ({
        type: UPDATE_GEOINFO_MULTIPOLYGON,
        uuid,
        points,
    });

export const updateGeoInfosPoint: (uuid: string, center: google.maps.LatLngLiteral, radius: number) => UpdateGeoInfosPointAction =
    (uuid, center, radius) => ({
        type: UPDATE_GEOINFO_POINT,
        uuid,
        center,
        radius,
    });

export const addGeoInfosBulk: (geoInfos: { [uuid: string]: GeographicInfo }) => AddGeoInfosBulkAction = (geoInfos) => ({
    type: ADD_GEOINFO_BULK,
    geoInfos,
});

export const deleteGeoInfos: (uuid: string) => DeleteGeoInfosAction = (uuid) => ({
    type: DELETE_GEOINFO,
    uuid: uuid as keyof MapReducerState,
});

export const setGEOJSON: (geoJson: GeoJsonData) => SetGEOJSONAction = (geoJson) => ({
    type: SET_GEOJSON,
    geoJson,
});

export const setGoogleMap: (map: google.maps.Map) => SetGoogleMapAction = (map) => ({
    type: SET_GOOGLE_MAP,
    map,
});
