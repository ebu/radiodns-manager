import Paper from '@material-ui/core/Paper';
import withStyles, {StyledComponentProps, StyleRulesCallback} from '@material-ui/core/styles/withStyles';
import {GoogleMap} from "@react-google-maps/api";
import React from 'react';
import {connect} from "react-redux";
import {API_KEY} from "../../config";
import {addGeoInfos, deleteGeoInfos, GeographicInfo, setEditing,} from "../../reducers/map-reducer";
import {RootReducerState} from "../../reducers/root-reducer";
import {uuidv4} from "../../utilities";
import {getCurrentPosition} from "../../utilities/geolocation";
import withRoot from "../../WithRoot";
import {CustomLoader} from "./CustomLoader";
import {MapPickerModuleType} from "./MapPickerModule";
import {MapPickerTypeSelector} from "./MapPickerTypeSelector";
import {PolygonModule} from "./PolygonModule";
import {MapPickerToolbox} from "./toolbox/MapPickerToolbox";

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
    editing?: boolean;
    addGeoInfos?: (uuid: string, geoInfo: GeographicInfo) => void;
    deleteGeoInfos?: (uuid: string) => void;
    setEditing?: (editing: boolean) => void;
}

interface State {
    pos: google.maps.LatLngLiteral | null;
    map: google.maps.Map | null;
}

class UnstyledMapPicker extends React.Component<Props, State> {

    public readonly state: State = {
        pos: null,
        map: null,
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
                <MapPickerTypeSelector
                    open={this.props.editing!}
                    onClose={this.handleOnCloseDialog}
                />
                <Paper className={classes.paper}>
                    <CustomLoader
                        id="script_loader"
                        googleMapsApiKey={API_KEY}
                    >
                        <GoogleMap
                            id='rdns_map_picker'
                            center={this.state.pos}
                            zoom={5}
                            mapTypeId="terrain"
                            onLoad={this.handleMapLoadEvent}
                            mapContainerStyle={{width: "100%", height: "100%"}}
                        >
                        </GoogleMap>
                    </CustomLoader>
                </Paper>
                <div className={classes.paper2}>
                    <MapPickerToolbox/>
                </div>
            </div>
        );
    }

    private handleMapLoadEvent = (map: google.maps.Map) => {
        this.setState({map});
    };

    private handleOnCloseDialog = (type: MapPickerModuleType | null) => {
        if (type && this.state.map) {
            const uuid = uuidv4();
            this.props.addGeoInfos!(uuid, {
                id: uuid,
                type: type,
                module: new PolygonModule().init(this.state.map),
            });
        }
        this.props.setEditing!(false);
    }
}

export const MapPicker = connect(
    (state: RootReducerState) => ({
        editing: state.map.editing,
        geoInfos: state.map.geoInfos,
    }),
    (dispatch) => ({
        setEditing: (editing: boolean) => dispatch(setEditing(editing)),
        addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => dispatch(addGeoInfos(uuid, geoInfo)),
        deleteGeoInfos: (uuid: string) => dispatch(deleteGeoInfos(uuid)),
    })
)(withRoot(withStyles(styles)(UnstyledMapPicker)));
