import {Action} from "redux";
import {MapPickerModule, MapPickerModuleType} from "../components/MapPicker/modules/MapPickerModule";
import {MarkerModuleOpts} from "../components/MapPicker/modules/MarkerModule";
import {PolygonModuleOpts} from "../components/MapPicker/modules/PolygonModule";
import {GEOJsonFeature} from "../geolocation/GEOJson";
// Types
const SET_EDITING = "radiodns-manager/map/SET_EDITING";
const SET_CURRENTLY_EDITED = "radiodns-manager/map/SET_CURRENTLY_EDITED";
const ADD_GEOINFO = "radiodns-manager/map/ADD_GEOINFO";
const DELETE_GEOINFO = "radiodns-manager/map/DELETE_GEOINFO";
const SET_GEOJSON = "radiodns-manager/map/SET_GEOJSON";
const SET_GOOGLE_MAP = "radiodns-manager/map/SET_GOOGLE_MAP";

interface SetEditingAction extends Action<typeof SET_EDITING> {
    editing: boolean;
}

interface AddGeoInfosAction extends Action<typeof ADD_GEOINFO> {
    uuid: string;
    geoInfo: GeographicInfo;
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
    SetEditingAction
    | SetGoogleMapAction
    | SetGEOJSONAction
    | DeleteGeoInfosAction
    | SetCurrentlyEditedAction
    | AddGeoInfosAction;

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
    editing: boolean;
    geoInfos: { [uuid: string]: GeographicInfo };
    currentlyEditedUuid: string;
    geoJson: GeoJsonData;
    map: google.maps.Map | null;
}

// Reducer
export const MAP_REDUCER_DEFAULT_STATE: MapReducerState = {
    editing: false,
    geoInfos: {},
    currentlyEditedUuid: "",
    geoJson: {
        polygons: [],
        status: "LOADING",
    },
    map: null,
};

const refreshCurrentlyEdited = (newState: MapReducerState) => {
    Object.values(newState.geoInfos).forEach((geoInfo) =>
        geoInfo.id === newState.currentlyEditedUuid ? geoInfo.module.onStartEdit() : geoInfo.module.onEditingStopped());
    return newState;
};

export function reducer(state: MapReducerState = MAP_REDUCER_DEFAULT_STATE, action: MapActions): MapReducerState {
    switch (action.type) {
        case SET_EDITING:
            return {...state, editing: action.editing};
        case SET_CURRENTLY_EDITED: {
            return refreshCurrentlyEdited({...state, currentlyEditedUuid: action.currentlyEditedUuid});
        }
        case ADD_GEOINFO:
            return {
                ...state,
                geoInfos: {...state.geoInfos, [action.uuid]: action.geoInfo},
                currentlyEditedUuid: action.uuid,
            };
        case SET_GEOJSON:
            return {...state, geoJson: action.geoJson};
        case DELETE_GEOINFO: {
            const {[action.uuid]: _, ...newState} = state;
            return newState as MapReducerState;
        }
        case SET_GOOGLE_MAP:
            return {...state, map: action.map};
        default:
            return state;
    }
}

// Action creators
export const setEditing: (editing: boolean) => SetEditingAction = (editing) => ({
    type: SET_EDITING,
    editing,
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

