import {Paper, StyledComponentProps, StyleRulesCallback} from "@material-ui/core";
import {Button} from "@material-ui/core/es";
import Typography from "@material-ui/core/es/Typography";
import withStyles from "@material-ui/core/styles/withStyles";
import * as React from "react";
import {connect} from "react-redux";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {GeographicInfo} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {GeoButton} from "./GeoButton";

const styles: StyleRulesCallback<any> = (theme) => ({
    toolboxPaper: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        marginTop: theme.spacing.unit,
        marginLeft: theme.spacing.unit,
        padding: `${theme.spacing.unit}px`,
    },
});

interface Props extends StyledComponentProps {
    geoInfos: { [uuid: string]: GeographicInfo };
    setActiveDialog: () => void;
}

const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
};

const MapPickerToolboxContainer: React.FunctionComponent<Props> = (props) => {

    return (
        <>
            <div onDragOver={handleDragOver}>
                {Object.keys(props.geoInfos).map((key) => (
                    <Paper key={key} className={props.classes!.toolboxPaper} draggable>
                        <GeoButton
                            key={key}
                            uuid={key}
                            type={props.geoInfos[key].rdnsType}
                        />
                    </Paper>
                ))}
            </div>
            {Object.keys(props.geoInfos).length === 0 &&
            <Paper className={props.classes!.toolboxPaper}>
                <Typography>Click on the + button</Typography>
            </Paper>}
            <Paper className={props.classes!.toolboxPaper} style={{marginTop: "auto"}}>
                <Button
                    type="button"
                    variant="contained"
                    color="primary"
                    onClick={props.setActiveDialog}
                >
                    +
                </Button>
            </Paper>
        </>
    );
};

export const MapPickerToolbox = connect(
    (state: RootReducerState) => ({
        geoInfos: state.map.geoInfos,
    }),
    (dispatch) => ({
        setActiveDialog: () => dispatch(setActiveDialog(Dialogs.TypeSelector)),
    }),
)(withStyles(styles)(MapPickerToolboxContainer));
