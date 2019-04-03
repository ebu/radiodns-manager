import Paper from '@material-ui/core/Paper';
import withStyles, {StyledComponentProps, StyleRulesCallback} from '@material-ui/core/styles/withStyles';
import React from 'react';
import {connect} from "react-redux";
import {API_KEY} from "../../config";
import {GeographicInfo, setGoogleMap} from "../../reducers/map-reducer";
import {RootReducerState} from "../../reducers/root-reducer";
import {getCurrentPosition} from "../../geolocation/geolocation";
import withRoot from "../../WithRoot";
import {DialogsHolder} from "./dialogs/DialogsHolder";
import {MapPickerToolbox} from "./toolbox/MapPickerToolbox";
import GoogleMapReact from "google-map-react";
import {InfoWindow} from "../map/InfoWindow";

const styles: StyleRulesCallback<any> = (theme) => ({
    main: {
        width: 'auto',
        display: 'flex',
        flexDirection: 'row',
        marginLeft: theme.spacing.unit,
        marginRight: theme.spacing.unit,
    },
    paper: {
        display: 'flex',
        marginTop: theme.spacing.unit,
        padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
        height: `calc(100vh - ${theme.spacing.unit * 10}px)`,
        width: "calc(100vw - 100px)",
    },
    paper2: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: "stretch",
    },
    toolboxPaper: {
        display: 'flex',
        justifyContent: "center",
        marginTop: theme.spacing.unit,
        marginLeft: theme.spacing.unit,
        padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
    },
    avatar: {
        margin: theme.spacing.unit,
        backgroundColor: theme.palette.secondary.main,
    },
});

interface Props extends StyledComponentProps {
    // injected
    geoInfos?: { [uuid: string]: GeographicInfo };
    setGoogleMap?: (map: google.maps.Map) => void;
}

interface State {
    pos: google.maps.LatLngLiteral | null;
}

class UnstyledMapPicker extends React.Component<Props, State> {

    public readonly state: State = {
        pos: null,
    };

    public async componentWillMount() {
        this.setState({pos: await getCurrentPosition()})
    }

    public render() {
        const {classes} = this.props;
        if (!classes || !this.state.pos) {
            return `${classes}/${this.state.pos}`
        }

        return (
            <div className={classes.main}>
                <DialogsHolder/>
                <Paper className={classes.paper}>
                    <GoogleMapReact
                        bootstrapURLKeys={{key: API_KEY}}
                        defaultCenter={this.state.pos}
                        defaultZoom={5}
                        yesIWantToUseGoogleMapApiInternals
                        onGoogleApiLoaded={this.handleMapLoadEvent}
                    >
                        {this.props.geoInfos && Object.values(this.props.geoInfos).map((geoInfo) => {
                            const center: google.maps.LatLngLiteral = geoInfo.module.returnCenter() || this.state.pos!;
                            return (
                                <InfoWindow
                                    lat={center.lat}
                                    lng={center.lng}
                                    key={geoInfo.id}
                                    geoInfo={geoInfo}
                                />
                            )
                        })}
                    </GoogleMapReact>
                </Paper>
                <div className={classes.paper2}>
                    <MapPickerToolbox/>
                </div>
            </div>
        );
    }

    private handleMapLoadEvent = (opts: { map: google.maps.Map, maps: any }) => {
        this.props.setGoogleMap!(opts.map);
    };
}

export const MapPicker = connect(
    (state: RootReducerState) => ({
        geoInfos: state.map.geoInfos,
    }),
    (dispatch) => ({
        setGoogleMap: (map: google.maps.Map) => dispatch(setGoogleMap(map)),
    })
)(withRoot(withStyles(styles)(UnstyledMapPicker)));
