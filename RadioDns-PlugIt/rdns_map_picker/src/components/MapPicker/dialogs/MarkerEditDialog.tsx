import * as React from 'react';
import {withStyles} from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import CloseIcon from '@material-ui/icons/Close';
import Slide from '@material-ui/core/Slide';
import {StyledComponentProps, StyleRulesCallback, TextField} from "@material-ui/core/es";
import {connect} from "react-redux";
import {RootReducerState} from "../../../reducers/root-reducer";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {addGeoInfos, GeographicInfo} from "../../../reducers/map-reducer";

const styles: StyleRulesCallback = (theme) => ({
    appBar: {
        position: "relative" as "relative",
    },
    flex: {
        flex: 1,
    },
    container: {
        display: 'flex',
        flexWrap: 'wrap',
    },
    textField: {
        marginLeft: theme.spacing.unit,
        marginRight: theme.spacing.unit,
        width: `calc(100vw - ${theme.spacing.unit * 2}px)`,
    },
});

const Transition: React.FunctionComponent = (props) => {
    return <Slide direction="up" {...props} />;
};

interface Props extends StyledComponentProps {
    // injected
    activeDialog?: Dialogs | null;
    closeThisDialog?: () => void;
    currentlyEdited?: string;
    geoInfos?: { [uuid: string]: GeographicInfo }
    addGeoInfos?: (uuid: string, geoInfo: GeographicInfo) => void;
}

interface State {
    label: string;
    textInfo: string;
}

class MarkerEditDialogContainer extends React.Component<Props, State> {

    constructor(props: Props) {
        super(props);
        this.state = {
            label: props.geoInfos![props.currentlyEdited!].module.getOptions().label || "",
            textInfo: props.geoInfos![props.currentlyEdited!].module.getOptions().textInfo || "",
        }
    }

    private handleClose = () => {
        this.props.closeThisDialog!();
    };

    private handleSave = () => {
        this.props.closeThisDialog!();
        const geoInfo = {...this.props.geoInfos![this.props.currentlyEdited!]};
        geoInfo.module.getOptions().label = this.state.label;
        geoInfo.module.getOptions().textInfo = this.state.textInfo;
        this.props.addGeoInfos!(geoInfo.id, geoInfo);
    };

    render() {
        const {classes} = this.props;
        return (
            <Dialog
                fullScreen
                open={true}
                onClose={this.handleClose}
                TransitionComponent={Transition}
            >
                <AppBar className={classes!.appBar}>
                    <Toolbar>
                        <IconButton color="inherit" onClick={this.handleClose} aria-label="Close">
                            <CloseIcon/>
                        </IconButton>
                        <Typography variant="h6" color="inherit" className={classes!.flex}>
                            RadioDNS marker attribute editor
                        </Typography>
                        <Button color="inherit" onClick={this.handleSave}>
                            save
                        </Button>
                    </Toolbar>
                </AppBar>
                <form className={classes!.container} noValidate autoComplete="off">
                    <List>
                        <TextField
                            name="label"
                            label="Name"
                            placeholder="Name of the marker"
                            margin="normal"
                            variant="outlined"
                            className={classes!.textField}
                            value={this.state.label}
                            onChange={this.onValueChange}
                        />
                        <Divider/>
                        <TextField
                            name="textInfo"
                            label="Text Info"
                            multiline
                            placeholder="Text information about the marker."
                            margin="normal"
                            variant="outlined"
                            className={classes!.textField}
                            value={this.state.textInfo}
                            onChange={this.onValueChange}
                        />
                    </List>
                </form>
            </Dialog>
        );
    }

    private onValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const name = e.target.name;
        const value = e.target.value;

        this.setState((prevState) => {
            const newState = {...prevState};
            newState[name as keyof State] = value;
            return newState;
        });
    }
}

export const MarkerEditDialog = connect(
    (state: RootReducerState) => ({
        activeDialog: state.dialog.activeDialog,
        currentlyEdited: state.map.currentlyEditedUuid,
        geoInfos: state.map.geoInfos,
    }),
    (dispatch) => ({
        closeThisDialog: () => dispatch(setActiveDialog(null)),
        addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => dispatch(addGeoInfos(uuid, geoInfo)),
    }),
)(withStyles(styles)(MarkerEditDialogContainer));