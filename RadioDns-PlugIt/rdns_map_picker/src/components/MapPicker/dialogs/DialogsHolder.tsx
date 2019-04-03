import * as React from "react";
import {connect} from "react-redux";
import {Dialogs} from "../../../reducers/dialog-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {CountrySelector} from "./CountrySelector";
import {TypeSelector} from "./TypeSelector";
import {MarkerEditDialog} from "./MarkerEditDialog";

interface Props {
    // injected
    activeDialog?: Dialogs | null;
}

const DialogsHolderContainer: React.FunctionComponent<Props> = (props) => (
    <>
        <TypeSelector
            open={props.activeDialog! === Dialogs.TypeSelector}
        />
        <CountrySelector
            open={props.activeDialog! === Dialogs.CountrySelector}
        />
        {props.activeDialog! === Dialogs.MarkerEdit && <MarkerEditDialog/>}
    </>
);

export const DialogsHolder = connect(
    (state: RootReducerState) => ({
        activeDialog: state.dialog.activeDialog,
    }),
)(DialogsHolderContainer);
