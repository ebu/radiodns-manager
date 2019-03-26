import {Paper, StyledComponentProps, StyleRulesCallback} from "@material-ui/core";
import {Button} from "@material-ui/core/es";
import Typography from "@material-ui/core/es/Typography";
import withStyles from "@material-ui/core/styles/withStyles";
import * as React from "react";
import {connect} from "react-redux";
import {GeographicInfo, setEditing} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {mapPickerTypeToIconAndText} from "../MapPickerModule";
import {GeoButton} from "./GeoButton";

const styles: StyleRulesCallback<any> = (theme) => ({
    toolboxPaper: {
        display: 'flex',
        flexDirection: "column",
        alignItems: "center",
        marginTop: theme.spacing.unit,
        marginLeft: theme.spacing.unit,
        padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
    },
    toolboxButton: {
        marginTop: `${theme.spacing.unit}px`,
    }
});

interface Props extends StyledComponentProps {
    geoInfos?: { [uuid: string]: GeographicInfo };
    setEditing?: () => void;
}

const MapPickerToolboxContainer: React.FunctionComponent<Props> = (props) => (
    <>
        <Paper className={props.classes!.toolboxPaper}>
            {Object.keys(props.geoInfos!).map((key) => (
                <GeoButton
                    key={key}
                    uuid={key}
                    className={props.classes!.toolboxButton}
                    type={props.geoInfos![key].type}
                />
            ))}
            {Object.keys(props.geoInfos!).length === 0 && <Typography>Click on the + button!</Typography>}
        </Paper>
        <Paper className={props.classes!.toolboxPaper} style={{marginTop: "auto"}}>
            <Button
                type="button"
                variant="contained"
                color="primary"
                onClick={props.setEditing}
            >
                +
            </Button>
        </Paper>
    </>
);
export const MapPickerToolbox = connect(
    (state: RootReducerState) => ({
        geoInfos: state.map.geoInfos
    }),
    (dispatch) => ({
        setEditing: () => dispatch(setEditing(true)),
    })
)(withStyles(styles)(MapPickerToolboxContainer));

