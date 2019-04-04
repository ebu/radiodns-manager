import {StyledComponentProps} from "@material-ui/core/es";
import Button from "@material-ui/core/es/Button";
import Card from "@material-ui/core/es/Card";
import CardActions from "@material-ui/core/es/CardActions";
import CardContent from "@material-ui/core/es/CardContent";
import withStyles from "@material-ui/core/es/styles/withStyles";
import Typography from "@material-ui/core/es/Typography";
import React from "react";
import {connect} from "react-redux";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {addGeoInfos, GeographicInfo} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {MapPickerModule} from "./modules/MapPickerModule";
import {MarkerModuleOpts} from "./modules/MarkerModule";
import {PolygonModuleOpts} from "./modules/PolygonModule";

const styles = {
    card: {
        display: "flex",
        flexDirection: "column" as "column",
        alignItems: "center",
        maxWidth: "250px",
        position: "absolute" as "absolute",
        left: "-50%",
        transform: "translate(-50%, -100%)",
        marginTop: "-50px",
    },
    arrowBottom: {
        width: 0,
        height: 0,
        borderLeft: "20px solid transparent",
        borderRight: "20px solid transparent",
        borderTop: "20px solid #ffffff",
    },
    pos: {
        fontSize: 12,
    },
};

interface Props extends StyledComponentProps {
    geoInfo: GeographicInfo;
    lat: number;
    lng: number;

    // injected
    setActiveDialog: () => void;
    current: string;
    modules: {[uuid: string]: MapPickerModule<MarkerModuleOpts | PolygonModuleOpts>};

}

interface State {
    dragged: boolean;
}

class InfoWindowContainer extends React.Component<Props> {

    public readonly state: State = {
        dragged: false,
    };

    private evtListenerStart: google.maps.MapsEventListener | null = null;
    private evtListenerEnd: google.maps.MapsEventListener | null = null;

    public componentWillUpdate(nextProps: Readonly<Props>): void {
        if (nextProps !== this.props && this.props.modules[this.props.geoInfo.id] !== undefined) {
            const module = this.props.modules[this.props.geoInfo.id];

            const item = module.getItem();
            if (item && this.evtListenerStart === null && this.evtListenerEnd === null) {
                this.evtListenerStart = item.addListener("dragstart", () => this.setState({dragged: true}));
                this.evtListenerEnd = item.addListener("dragend", () => this.setState({dragged: false}));
            }
        }
    }

    public componentWillUnmount(): void {
        if (this.evtListenerStart) {
            this.evtListenerStart.remove();
            this.evtListenerStart = null;
        }

        if (this.evtListenerEnd) {
            this.evtListenerEnd.remove();
            this.evtListenerStart = null;
        }
    }

    public render() {
        const {classes, geoInfo} = this.props;
        const textInfo = geoInfo.textInfo || "";
        const label = geoInfo.label;

        if (!label || this.props.current !== geoInfo.id || this.state.dragged) {
            return null;
        }

        return (
            <div
                className={classes!.card}
                onMouseEnter={this.handleMouseEnter}
                onMouseLeave={this.handleMouseLeave}
            >
                <Card>
                    <CardContent>
                        <Typography component="h6">
                            {label}
                        </Typography>
                        <Typography className={classes!.pos} color="textSecondary">
                            {textInfo.length > 25 ? textInfo.substring(0, 25) + "..." : textInfo}
                        </Typography>
                    </CardContent>
                    <CardActions>
                        <Button size="small" onClick={this.props.setActiveDialog}>Edit</Button>
                    </CardActions>
                </Card>
                <div className={classes!.arrowBottom}/>
            </div>
        );
    }

    private handleMouseEnter = () => Object.values(this.props.modules)
        .forEach((module) => module.disableActiveListener());

    private handleMouseLeave = () => Object.values(this.props.modules)
        .forEach((module) => module.enableActiveListener());
}

export const InfoWindow = connect(
    (state: RootReducerState) => ({
        current: state.map.currentlyEditedUuid,
        modules: state.googleModule.modules,
    }),
    (dispatch) => ({
        setActiveDialog: () => dispatch(setActiveDialog(Dialogs.MarkerEdit)),
        addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => dispatch(addGeoInfos(uuid, geoInfo)),
    }),
)(withStyles(styles)(InfoWindowContainer));
