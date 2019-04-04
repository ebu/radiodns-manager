import ListItemText from "@material-ui/core/es/ListItemText";
import * as React from "react";
import {connect} from "react-redux";
import {GEOJsonFeature} from "../../../geolocation/GEOJson";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {
    addGeoInfos,
    GeographicInfo,
    GeoJsonData,
    ModuleType,
    RdnsType,
    setCurrentlyEdited,
} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {uuidv4} from "../../../utilities";
import {DialogBase} from "./DialogBase";

interface Props {
    open: boolean;

    // injected
    geoJson: GeoJsonData;
    map: google.maps.Map | null;

    addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => void;
    setActiveDialog: (activeDialog: Dialogs | null) => void;
    setCurrentlyEdited: (currentlyEditedUuid: string) => void;
}

const getDataKey = (data: GEOJsonFeature) => data.properties.ADMIN || "";

const renderData = (data: GEOJsonFeature) => {
    return (
        <ListItemText primary={data.properties.ADMIN}/>
    );
};

const CountrySelectorContainer: React.FunctionComponent<Props> = (props) => {
    const handleOnClose = (geojson: GEOJsonFeature | null) => {
        if (geojson) {
            const uuid = uuidv4();
            const opts = {
                id: uuid,
                rdnsType: RdnsType.Country,
                label: "",
                textInfo: "",
                injected: true,
            };
            let points: google.maps.LatLngLiteral[][] = [];
            switch (geojson.geometry.type) {
                case "MultiPolygon":
                    points = geojson.geometry.coordinates
                        .flatMap((n1) => n1
                            .map((n2) => n2
                                .map((pointTuple) => ({lat: pointTuple[1], lng: pointTuple[0]}))));
                    break;
                case "Polygon":
                    points = [geojson.geometry.coordinates[0].map((pointTuple) => ({
                        lat: pointTuple[1],
                        lng: pointTuple[0],
                    }))];
                    break;
            }
            props.addGeoInfos(uuid, {...opts, geoData: {
                    type: ModuleType.MultiPolygon,
                    points,
                }});
        }
        props.setActiveDialog!(null);
    };

    return (
        <DialogBase
            title="Choose a country"
            data={props.geoJson.polygons}
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
    }),
)(CountrySelectorContainer);
