import ListItemText from "@material-ui/core/es/ListItemText";
import * as React from "react";
import {connect} from "react-redux";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {addGeoInfos, GeographicInfo, GeoJsonData, setCurrentlyEdited} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {uuidv4} from "../../../utilities";
import {GEOJsonFeature} from "../../../geolocation/GEOJson";
import {MapPickerModuleType} from "../modules/MapPickerModule";
import {PolygonModule} from "../modules/PolygonModule";
import {DialogBase} from "./DialogBase";

interface Props {
    open: boolean;

    // injected
    geoJson?: GeoJsonData;
    map?: google.maps.Map | null;

    addGeoInfos?: (uuid: string, geoInfo: GeographicInfo) => void;
    setActiveDialog?: (activeDialog: Dialogs | null) => void;
    setCurrentlyEdited?: (currentlyEditedUuid: string) =>  void;
}

const getDataKey = (data: GEOJsonFeature) => data.properties.ADMIN;

const renderData = (data: GEOJsonFeature) => {
    return (
        <ListItemText primary={data.properties.ADMIN}/>
    );
};

const CountrySelectorContainer: React.FunctionComponent<Props> = (props) => {
    const handleOnClose = (geojson: GEOJsonFeature | null) => {
        if (geojson && props.map) {
            const uuid = uuidv4();
            const paths = geojson.geometry.type === "Polygon"
                ? geojson.geometry.coordinates[0].map((pointTuple) => ({lat: pointTuple[1], lng: pointTuple[0]}))
                : geojson.geometry.coordinates.flatMap((n1) => n1.map((n2) => n2.map((pointTuple) => ({lat: pointTuple[1], lng: pointTuple[0]}))));
            props.addGeoInfos!(uuid, {
                id: uuid,
                type: MapPickerModuleType.Country,
                module:  new PolygonModule({
                    map: props.map,
                    paths, noClick: true,
                    setActive: () => props.setCurrentlyEdited!(uuid),
                    editable: false,
                    draggable: false,
                    openDeleteMenu: () => {},
                }),
            });
        }
        props.setActiveDialog!(null);
    };

    return (
        <DialogBase
            title="Choose a country"
            data={props.geoJson!.polygons}
            open={props.open}
            getDataKey={getDataKey}
            renderData={renderData}
            searchFieldTitle={"Country"}
            onClose={handleOnClose}
        />
    );
};

export const CountrySelector = connect(
    (state: RootReducerState) => ({
        geoJson: state.map.geoJson,
        map: state.map.map,
    }),
    (dispatch) => ({
        addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => dispatch(addGeoInfos(uuid, geoInfo)),
        setActiveDialog: (activeDialog: Dialogs | null) => dispatch(setActiveDialog(activeDialog)),
        setCurrentlyEdited: (currentlyEditedUuid: string) => dispatch(setCurrentlyEdited(currentlyEditedUuid)),
    })
)(CountrySelectorContainer);
