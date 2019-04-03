import {createStyles, StyledComponentProps, withStyles} from "@material-ui/core";
import {Button} from "@material-ui/core/es";
import IconButton from "@material-ui/core/es/IconButton";
import Menu from "@material-ui/core/es/Menu";
import MenuItem from "@material-ui/core/es/MenuItem";
import {MoreVert} from "@material-ui/icons";
import * as React from "react";
import {connect} from "react-redux";
import {deleteGeoInfos, setCurrentlyEdited} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {MapPickerModuleType, mapPickerTypeToIconAndText} from "../modules/MapPickerModule";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";

const styles = createStyles({
    menuButtonContainer: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "center",
        alignItems: "center",
    },
    menu: {
        marginLeft: "5px",
        padding: "0px",
    }
});

interface Props extends StyledComponentProps {
    uuid: string;
    className?: string;
    type: MapPickerModuleType;

    // injected
    deleteGeoInfos?: () => void;
}

interface InjectedProps extends Props {
    currentlyEditedUuid?: string;
    setCurrentlyEdited?: () => void;
    setActiveDialog: (dialog: Dialogs | null) => void;
}

const options = [
    "Add / Set Label",
    "Delete",
];

const ITEM_HEIGHT = 48;

const GeoButtonContainer: React.FunctionComponent<InjectedProps> = (props) => {
    const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);
    const open = Boolean(anchorEl);

    function handleClick(event: React.MouseEvent<HTMLElement, MouseEvent>) {
        setAnchorEl(event.currentTarget);
    }

    function handleClose(option?: string) {
        switch (option) {
            case "Delete":
                props.deleteGeoInfos!();
                break;
            case "Add / Set Label":
                props.setCurrentlyEdited!();
                props.setActiveDialog!(Dialogs.MarkerEdit);
                break;
        }
        setAnchorEl(null);
    }

    return (
        <div key={props.uuid} className={props.classes!.menuButtonContainer}>
            <Button
                type="button"
                variant={props.uuid === props.currentlyEditedUuid ? "contained" : "outlined"}
                color="secondary"
                className={props.className}
                onClick={props.setCurrentlyEdited}
            >
                {mapPickerTypeToIconAndText(props.type).icon}
            </Button>
            <IconButton
                className={props.classes!.menu}
                aria-label="More"
                aria-owns={open ? 'long-menu' : undefined}
                aria-haspopup="true"
                onClick={handleClick}
            >
                <MoreVert/>
            </IconButton>
            <Menu
                id="long-menu"
                anchorEl={anchorEl}
                open={open}
                onClose={() => handleClose()}
                PaperProps={{
                    style: {
                        maxHeight: ITEM_HEIGHT * 4.5,
                        width: 200,
                    },
                }}
            >
                {options.map(option => (
                    <MenuItem key={option} onClick={() => handleClose(option)}>
                        {option}
                    </MenuItem>
                ))}
            </Menu>
        </div>
    );
};

export const GeoButton = connect((state: RootReducerState) => ({
        currentlyEditedUuid: state.map.currentlyEditedUuid,
    }),
    ((dispatch, ownProps: Props) => ({
        setCurrentlyEdited: () => dispatch(setCurrentlyEdited(ownProps.uuid)),
        deleteGeoInfos: () => dispatch(deleteGeoInfos(ownProps.uuid)),
        setActiveDialog: (dialog: Dialogs | null) => dispatch(setActiveDialog(dialog)),
    }))
)(withStyles(styles)(GeoButtonContainer));
