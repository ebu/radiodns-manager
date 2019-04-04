import {combineReducers, createStore} from "redux";
import {getGeoJson} from "../geolocation/GEOJson";
import {DIALOG_REDUCER_DEFAULT_STATE, DialogReducerState, reducer as dialog} from "./dialog-reducer";
import {
    GOOGLE_MODULE_REDUCER_DEFAULT_STATE,
    GoogleModuleReducerState,
    reducer as googleModule,
} from "./google-module-reducers";
import {MAP_REDUCER_DEFAULT_STATE, MapReducerState, reducer as map, setGEOJSON} from "./map-reducer";

export interface RootReducerState {
    map: MapReducerState;
    dialog: DialogReducerState;
    googleModule: GoogleModuleReducerState,
}

export const store = createStore(
    combineReducers<RootReducerState>({
        map,
        dialog,
        googleModule,
    }),
    {
        map: MAP_REDUCER_DEFAULT_STATE,
        dialog: DIALOG_REDUCER_DEFAULT_STATE,
        googleModule: GOOGLE_MODULE_REDUCER_DEFAULT_STATE,
    },
);

getGeoJson()
    .then((polygons) => store.dispatch(setGEOJSON({
        polygons,
        status: "COMPLETED",
    })))
    .catch((e) => {
        console.warn("GEOJSON parsing failed!", e);
        store.dispatch(setGEOJSON({
            polygons: [],
            status: "FAILED",
        }))
    });
