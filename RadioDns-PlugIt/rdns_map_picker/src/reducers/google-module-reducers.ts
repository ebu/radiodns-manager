import {Action} from "redux";
import {MapPickerModule} from "../components/map/google/modules/MapPickerModule";
import {MarkerModuleOpts} from "../components/map/google/modules/MarkerModule";
import {PolygonModuleOpts} from "../components/map/google/modules/PolygonModule";
import {objectWithoutProperties} from "../utilities";

// Types
const REGISTER_MODULE = "radiodns-manager/google-module/REGISTER_MODULE";
const UNREGISTER_MODULE = "radiodns-manager/google-module/UNREGISTER_MODULE";

interface RegisterModuleAction extends Action<typeof REGISTER_MODULE> {
    module: MapPickerModule<MarkerModuleOpts | PolygonModuleOpts>;
}

interface UnregisterModuleAction extends Action<typeof UNREGISTER_MODULE> {
    uuid: string;
}

type GoogleModuleReducerActions =
    | RegisterModuleAction
    | UnregisterModuleAction;

export interface GoogleModuleReducerState {
    modules: {[uuid: string]: MapPickerModule<MarkerModuleOpts | PolygonModuleOpts>};
}

// Reducer
export const GOOGLE_MODULE_REDUCER_DEFAULT_STATE: GoogleModuleReducerState = {
    modules: {},
};

export function reducer(state: GoogleModuleReducerState = GOOGLE_MODULE_REDUCER_DEFAULT_STATE,
                        action: GoogleModuleReducerActions): GoogleModuleReducerState {
    switch (action.type) {
        case REGISTER_MODULE:
            return {...state, modules: {...state.modules, [action.module.getOptions().uuid]: action.module}};
        case UNREGISTER_MODULE: {
            const newState = {...state};
            newState.modules = objectWithoutProperties(newState.modules, [action.uuid]);
            return newState;
        }
        default:
            return state;
    }
}

// Action creators
export const registerGoogleModule: (module: MapPickerModule<MarkerModuleOpts | PolygonModuleOpts>) => RegisterModuleAction = (module) => ({
    type: REGISTER_MODULE,
    module,
});

export const unregisterGoogleModule: (uuid: string) => UnregisterModuleAction = (uuid) => ({
    type: UNREGISTER_MODULE,
    uuid,
});
