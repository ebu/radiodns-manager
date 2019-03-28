import {combineReducers, createStore} from "redux";
import {getGeoJson} from "../geolocation/GEOJson";
import {DIALOG_REDUCER_DEFAULT_STATE, DialogReducerState, reducer as dialog} from "./dialog-reducer";
import {MAP_REDUCER_DEFAULT_STATE, MapReducerState, reducer as map, setGEOJSON} from "./map-reducer";

export interface RootReducerState {
    map: MapReducerState;
    dialog: DialogReducerState;
}

export const store = createStore(
    combineReducers<RootReducerState>({
        map,
        dialog,
    }),
    {
        map: MAP_REDUCER_DEFAULT_STATE,
        dialog: DIALOG_REDUCER_DEFAULT_STATE,
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
