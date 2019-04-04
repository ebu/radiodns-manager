import * as React from "react";
import {connect} from "react-redux";
import {registerGoogleModule, unregisterGoogleModule} from "../../../reducers/google-module-reducers";
import {
    GeographicInfo,
    ModuleType,
    RdnsType,
    setCurrentlyEdited,
    updateGeoInfosMultiPolygons, updateGeoInfosPoint,
} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {MapPickerModule} from "./modules/MapPickerModule";
import {MarkerModule, MarkerModuleOpts} from "./modules/MarkerModule";
import {PolygonModule, PolygonModuleOpts} from "./modules/PolygonModule";

interface Props {
    geoInfo: GeographicInfo;
    map: google.maps.Map;

    // injected
    currentlyEditedUuid: string;
    setActive: (uuid: string) => () => void;
    updateGeoInfosMultiPolygons: (uuid: string, points: google.maps.LatLngLiteral[][]) => void;
    updateGeoInfosPoint: (uuid: string, center: google.maps.LatLngLiteral, radius: number) => void;
    registerGoogleModule: (module: MapPickerModule<MarkerModuleOpts | PolygonModuleOpts>) => void;
    unregisterGoogleModule: (uuid: string) => void;
}

class ModuleHolderContainer extends React.Component<Props> {
    private module: PolygonModule | MarkerModule;

    constructor(props: Props) {
        super(props);

        const {geoData, id, rdnsType, label, textInfo, injected} = props.geoInfo;

        switch (geoData.type) {
            case ModuleType.MultiPolygon:
                this.module = new PolygonModule({
                    uuid: props.geoInfo.id,
                    draggable: rdnsType !== RdnsType.Country,
                    editable: rdnsType !== RdnsType.Country,
                    label,
                    textInfo,
                    map: props.map,
                    noClick: injected,
                    setActive: props.setActive!(id),
                    paths: geoData.points,
                    updateGeoInfosMultiPolygons: props.updateGeoInfosMultiPolygons,
                }).init();
                break;
            default:
                this.module = new MarkerModule({
                    uuid: props.geoInfo.id,
                    label,
                    textInfo,
                    map: props.map,
                    noClick: injected,
                    setActive: props.setActive!(id),
                    editable: true,
                    draggable: true,
                    position: geoData.center,
                    circleRadius: geoData.radius !== 0 ? geoData.radius : undefined,
                    updateGeoInfosPoint: props.updateGeoInfosPoint,
                }).init();
                break;
        }
    }

    public componentWillMount(): void {
        this.props.registerGoogleModule(this.module);
    }

    public componentWillUnmount(): void {
        this.props.unregisterGoogleModule(this.module.getOptions().uuid);
    }

    public componentDidUpdate(prevProps: Readonly<Props>): void {
        if (prevProps !== this.props) {
            if (this.props.currentlyEditedUuid === this.props.geoInfo.id) {
                this.module.onStartEdit();
            } else {
                this.module.onEditingStopped();
            }
            if (prevProps.map !== this.props.map) {
                this.module.setMap(this.props.map);
            }
        }
    }

    public render() {
        return null;
    }
}

export const ModuleHolder = connect(
    (state: RootReducerState) => ({
        currentlyEditedUuid: state.map.currentlyEditedUuid,
    }),
    (dispatch) => ({
        setActive: (uuid: string) => () => dispatch(setCurrentlyEdited(uuid)),
        updateGeoInfosMultiPolygons: (uuid: string, points: google.maps.LatLngLiteral[][]) => dispatch(updateGeoInfosMultiPolygons(uuid, points)),
        updateGeoInfosPoint: (uuid: string, center: google.maps.LatLngLiteral, radius: number) => dispatch(updateGeoInfosPoint(uuid, center, radius)),
        registerGoogleModule: (module: MapPickerModule<MarkerModuleOpts | PolygonModuleOpts>) => dispatch(registerGoogleModule(module)),
        unregisterGoogleModule: (uuid: string) => dispatch(unregisterGoogleModule(uuid)),
    }),
)(ModuleHolderContainer);
