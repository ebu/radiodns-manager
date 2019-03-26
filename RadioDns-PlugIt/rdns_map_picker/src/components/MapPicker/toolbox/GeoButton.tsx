import {Button} from "@material-ui/core/es";
import * as React from "react";
import {connect} from "react-redux";
import {setCurrentlyEdited} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {MapPickerModuleType, mapPickerTypeToIconAndText} from "../MapPickerModule";

interface Props {
    uuid: string;
    className?: string;
    type: MapPickerModuleType;
}

interface InjectedProps extends Props {
    currentlyEditedUuid?: string;
    setCurrentlyEdited?: () => void;
}

const GeoButtonContainer: React.FunctionComponent<InjectedProps> = (props) => (
    <Button
        key={props.uuid}
        type="button"
        variant={props.uuid === props.currentlyEditedUuid ? "contained" : "outlined"}
        color="secondary"
        className={props.className}
        onClick={props.setCurrentlyEdited}
    >
        {mapPickerTypeToIconAndText(props.type).icon}
    </Button>
);

export const GeoButton = connect((state: RootReducerState) => ({
        currentlyEditedUuid: state.map.currentlyEditedUuid,
    }),
    ((dispatch, ownProps: Props) => ({
        setCurrentlyEdited: () => dispatch(setCurrentlyEdited(ownProps.uuid))
    }))
)(GeoButtonContainer);
