import {Action} from "redux";

export enum Dialogs {
    CountrySelector,
    TypeSelector,
}

// Types
const SET_ACTIVE_DIALOG = "radiodns-manager/dialog/SET_ACTIVE_DIALOG";

interface SetActiveDialogAction extends Action<typeof SET_ACTIVE_DIALOG> {
    activeDialog: Dialogs | null;
}

type DialogActions = SetActiveDialogAction;

export interface DialogReducerState {
    activeDialog: Dialogs | null;
}

// Reducer
export const DIALOG_REDUCER_DEFAULT_STATE: DialogReducerState = {
    activeDialog: null,
};

export function reducer(state: DialogReducerState = DIALOG_REDUCER_DEFAULT_STATE, action: DialogActions): DialogReducerState {
    switch (action.type) {
        case SET_ACTIVE_DIALOG:
            return {...state, activeDialog: action.activeDialog};
        default:
            return state;
    }
}

// Action creators
export const setActiveDialog: (activeDialog: Dialogs | null) => SetActiveDialogAction = (activeDialog) => ({
    type: SET_ACTIVE_DIALOG,
    activeDialog,
});
