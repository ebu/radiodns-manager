import {Action} from "redux";
import {MapPickerModule, MapPickerModuleType} from "../components/MapPicker/modules/MapPickerModule";
import {MarkerModuleOpts} from "../components/MapPicker/modules/MarkerModule";
import {PolygonModuleOpts} from "../components/MapPicker/modules/PolygonModule";
import {GEOJsonFeature} from "../geolocation/GEOJson";
import {objectWithoutProperties} from "../utilities";

// Types
const SET_CURRENTLY_EDITED = "radiodns-manager/map/SET_CURRENTLY_EDITED";
const ADD_GEOINFO = "radiodns-manager/map/ADD_GEOINFO";
const ADD_GEOINFO_BULK = "radiodns-manager/map/ADD_GEOINFO_BULK";
const DELETE_GEOINFO = "radiodns-manager/map/DELETE_GEOINFO";
const SET_GEOJSON = "radiodns-manager/map/SET_GEOJSON";
const SET_GOOGLE_MAP = "radiodns-manager/map/SET_GOOGLE_MAP";

interface AddGeoInfosAction extends Action<typeof ADD_GEOINFO> {
    uuid: string;
    geoInfo: GeographicInfo;
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
    | SetGoogleMapAction
    | SetGEOJSONAction
    | DeleteGeoInfosAction
    | SetCurrentlyEditedAction
    | AddGeoInfosAction
    | AddGeoInfosBulkAction;

export interface GeographicInfo {
    id: string;
    type: MapPickerModuleType;
    module: MapPickerModule<PolygonModuleOpts | MarkerModuleOpts>;
}

export interface GeoJsonData {
    polygons: GEOJsonFeature[];
    status: "LOADING" | "FAILED" | "COMPLETED";
}

export interface MapReducerState {
    geoInfos: { [uuid: string]: GeographicInfo };
    currentlyEditedUuid: string;
    geoJson: GeoJsonData;
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
    map: null,
};

const refreshCurrentlyEdited = (newState: MapReducerState) => {
    let geoInfos: GeographicInfo[] = Object.values(newState.geoInfos)
        .filter((geoInfo) => geoInfo.id !== newState.currentlyEditedUuid);

    const first = Object.values(newState.geoInfos).find((geoInfo) => geoInfo.id === newState.currentlyEditedUuid);
    if (first) {
        geoInfos = [first, ...geoInfos];
    }

    geoInfos.forEach((geoInfo) =>
        geoInfo.id === newState.currentlyEditedUuid
            ? geoInfo.module.onStartEdit()
            : geoInfo.module.onEditingStopped());
    return newState;
};

export function reducer(state: MapReducerState = MAP_REDUCER_DEFAULT_STATE, action: MapActions): MapReducerState {
    switch (action.type) {
        case SET_CURRENTLY_EDITED: {
            return refreshCurrentlyEdited({...state, currentlyEditedUuid: action.currentlyEditedUuid});
        }
        case ADD_GEOINFO:
            return {
                ...state,
                geoInfos: {...state.geoInfos, [action.uuid]: action.geoInfo},
                currentlyEditedUuid: action.uuid,
            };

        case ADD_GEOINFO_BULK: {
            return {
                ...state,
                geoInfos: {...state.geoInfos, ...action.geoInfos}
            };
        }
        case DELETE_GEOINFO: {
            const newState = {...state};
            newState.geoInfos[action.uuid].module.onDelete();
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

export const setCurrentlyEdited: (currentlyEditedUuid: string) => SetCurrentlyEditedAction = (currentlyEditedUuid) => ({
    type: SET_CURRENTLY_EDITED,
    currentlyEditedUuid: currentlyEditedUuid as keyof MapReducerState,
});

export const addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => AddGeoInfosAction = (uuid, geoInfo) => ({
    type: ADD_GEOINFO,
    uuid,
    geoInfo,
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

