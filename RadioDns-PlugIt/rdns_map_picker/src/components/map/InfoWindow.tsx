import React from 'react';
import Typography from "@material-ui/core/es/Typography";
import {StyledComponentProps} from "@material-ui/core/es";
import Card from "@material-ui/core/es/Card";
import CardContent from "@material-ui/core/es/CardContent";
import CardActions from "@material-ui/core/es/CardActions";
import Button from "@material-ui/core/es/Button";
import withStyles from "@material-ui/core/es/styles/withStyles";
import {connect} from "react-redux";
import {RootReducerState} from "../../reducers/root-reducer";
import {addGeoInfos, GeographicInfo} from "../../reducers/map-reducer";
import {Dialogs, setActiveDialog} from "../../reducers/dialog-reducer";

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
    geoInfos?: { [uuid: string]: GeographicInfo };
    setActiveDialog?: () => void;
    current?: string;
    addGeoInfos?: (uuid: string, geoInfo: GeographicInfo) => void;
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

    public componentWillMount(): void {
        const module = this.props.geoInfo!.module;

        const item = module.getItem();
        if (item) {
            this.evtListenerStart = item.addListener("dragstart", () => this.setState({dragged: true}));
            this.evtListenerEnd = item.addListener("dragend", () => {
                this.setState({dragged: false});
                const newGeoInfo = {...this.props.geoInfo};
                newGeoInfo.module.modifiedFlag = !newGeoInfo.module.modifiedFlag;
                this.props.addGeoInfos!(newGeoInfo.id, newGeoInfo);
            });
        }
    }

    public componentWillUnmount(): void {
        if (this.evtListenerStart) {
            this.evtListenerStart.remove();
        }

        if (this.evtListenerEnd) {
            this.evtListenerEnd.remove();
        }
    }

    public render() {
        const {classes, geoInfo, setActiveDialog} = this.props;
        const textInfo = geoInfo.module.getOptions().textInfo || "";
        const label = geoInfo.module.getOptions().label;

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
                        <Button size="small" onClick={setActiveDialog}>Edit</Button>
                    </CardActions>
                </Card>
                <div className={classes!.arrowBottom}/>
            </div>
        );
    }

    private handleMouseEnter = () => Object.values(this.props.geoInfos!)
        .forEach((geoInfo) => geoInfo.module.disableActiveListener());

    private handleMouseLeave = () => Object.values(this.props.geoInfos!)
        .forEach((geoInfo) => geoInfo.module.enableActiveListener());
}

export const InfoWindow = connect(
    (state: RootReducerState) => ({
        geoInfos: state.map.geoInfos,
        current: state.map.currentlyEditedUuid,
    }),
    (dispatch) => ({
        setActiveDialog: () => dispatch(setActiveDialog(Dialogs.MarkerEdit)),
        addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => dispatch(addGeoInfos(uuid, geoInfo)),
    }),
)(withStyles(styles)(InfoWindowContainer));
