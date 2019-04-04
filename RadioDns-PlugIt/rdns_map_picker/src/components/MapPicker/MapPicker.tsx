import Paper from "@material-ui/core/Paper";
import withStyles, {StyledComponentProps, StyleRulesCallback} from "@material-ui/core/styles/withStyles";
import GoogleMapReact from "google-map-react";
import React from "react";
import {Map, TileLayer} from "react-leaflet";
import {connect} from "react-redux";
import {API_KEY} from "../../config";
import {getCurrentPosition} from "../../geolocation/geolocation";
import {GeographicInfo, MapProvider, setGoogleMap} from "../../reducers/map-reducer";
import {RootReducerState} from "../../reducers/root-reducer";
import withRoot from "../../WithRoot";
import {InfoWindow} from "../map/google/InfoWindow";
import {ModuleHolder} from "../map/google/ModuleHolder";
import {MarkerFactory} from "../map/open-street-map/MarkerFactory";
import {DialogsHolder} from "./dialogs/DialogsHolder";
import {MapPickerToolbox} from "./toolbox/MapPickerToolbox";
import {getCenterOfGeoData} from "./utilities";

const styles: StyleRulesCallback<any> = (theme) => ({
    main: {
        width: "auto",
        display: "flex",
        flexDirection: "row",
        marginLeft: theme.spacing.unit,
        marginRight: theme.spacing.unit,
    },
    paper: {
        display: "flex",
        marginTop: theme.spacing.unit,
        padding: `${theme.spacing.unit}px ${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
        height: `calc(100vh - ${theme.spacing.unit * 10}px)`,
        width: "calc(100vw - 100px)",
    },
    paper2: {
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
    },
    toolboxPaper: {
        display: "flex",
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
    mapProvider?: MapProvider;
    map?: google.maps.Map | null;
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
        const {classes, map, geoInfos} = this.props;
        if (!classes || !this.state.pos) {
            return "loading...";
        }

        return (
            <div className={classes.main}>
                <DialogsHolder/>
                <Paper className={classes.paper}>
                    {this.props.mapProvider === MapProvider.Google && <GoogleMapReact
                        bootstrapURLKeys={{key: API_KEY}}
                        defaultCenter={this.state.pos}
                        defaultZoom={5}
                        yesIWantToUseGoogleMapApiInternals
                        onGoogleApiLoaded={this.handleMapLoadEvent}
                    >
                        {map && geoInfos && Object.values(geoInfos).map((geoInfo) => {
                            const center = getCenterOfGeoData(geoInfo.geoData, this.state.pos!);
                            return [
                                <ModuleHolder
                                    key={geoInfo.id}
                                    geoInfo={geoInfo}
                                    map={map}
                                />,
                                <InfoWindow
                                    key={"w" + geoInfo.id}
                                    lat={center.lat}
                                    lng={center.lng}
                                    geoInfo={geoInfo}
                                />,
                            ];
                        })}
                    </GoogleMapReact>}
                    {this.props.mapProvider === MapProvider.OpenStreetMaps &&
                    <Map
                        center={[this.state.pos!.lat, this.state.pos!.lng]}
                        zoom={5}
                        className={classes.paper}
                    >
                        <TileLayer
                            attribution='&amp;copy <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        {geoInfos && Object.values(geoInfos).map((geoInfo) => {
                            const center = getCenterOfGeoData(geoInfo.geoData, this.state.pos!);
                            return [
                                <MarkerFactory geoInfo={geoInfo} key={geoInfo.id}/>,
                            ];
                        })}
                    </Map>}
                </Paper>
                <div className={classes.paper2}>
                    <MapPickerToolbox/>
                </div>
            </div>
        );
    }

    private handleMapLoadEvent = (opts: { map: google.maps.Map, maps: any }) => {
        console.log("SETTING MAP", opts.map);
        this.props.setGoogleMap!(opts.map);
    };
}

export const MapPicker = connect(
    (state: RootReducerState) => ({
        geoInfos: state.map.geoInfos,
        map: state.map.map,
        mapProvider: state.map.mapProvider,
    }),
    (dispatch) => ({
        setGoogleMap: (map: google.maps.Map) => dispatch(setGoogleMap(map)),
    }),
)(withRoot(withStyles(styles)(UnstyledMapPicker)));
