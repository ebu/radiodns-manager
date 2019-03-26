import {combineReducers, createStore} from "redux";
import {MAP_REDUCER_DEFAULT_STATE, MapReducerState, reducer as map} from "./map-reducer";

export interface RootReducerState {
    map: MapReducerState;
}

export const ROOT_REDUCER_INITIAL_STATE = {
    map: MAP_REDUCER_DEFAULT_STATE,
};

export const store = createStore(
    combineReducers<RootReducerState>({
        map
    }),
    ROOT_REDUCER_INITIAL_STATE,
);
