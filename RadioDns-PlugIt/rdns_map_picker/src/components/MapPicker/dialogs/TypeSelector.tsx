import {ListItemAvatar} from "@material-ui/core";
import Avatar from "@material-ui/core/es/Avatar";
import ListItemText from "@material-ui/core/es/ListItemText";
import * as React from "react";
import {connect} from "react-redux";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {
    addGeoInfos,
    deleteGeoInfos,
    GeographicInfo,
    ModuleType,
    RdnsType,
    setCurrentlyEdited,
} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {uuidv4} from "../../../utilities";
import {mapPickerTypeToIconAndText} from "../../map/google/modules/MapPickerModule";
import {getMetersPerPixel} from "../utilities";
import {DialogBase} from "./DialogBase";

interface Props {
    open: boolean;

    // injected
    map: google.maps.Map | null;
    addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => void;
    deleteGeoInfos: (uuid: string) => void;
    setActiveDialog: (activeDialog: Dialogs | null) => void;
    setCurrentlyEdited: (currentlyEditedUuid: string) =>  void;
}

const getDataKey = (data: RdnsType) => data;

const renderData = (data: RdnsType) => {
    const {icon, text} = mapPickerTypeToIconAndText(data);
    return (
        <>
            <ListItemAvatar>
                <Avatar>
                    {icon}
                </Avatar>
            </ListItemAvatar>
            <ListItemText primary={text}/>
        </>
    );
};

const TypeSelectorContainer: React.FunctionComponent<Props> = (props) => {

    const handleOnClose = (type: RdnsType | null) => {
        if (type && props.map) {
            const uuid = uuidv4();

            switch (type) {
                case RdnsType.Headquarters:
                    props.addGeoInfos(uuid, {
                        id: uuid,
                        rdnsType: type,
                        geoData: {
                            type: ModuleType.Point,
                            radius: 0,
                        },
                        injected: false,
                        textInfo: "",
                        label: "",
                    });
                    props.setActiveDialog(null);
                    break;
                case RdnsType.Channel:
                    props.addGeoInfos(uuid, {
                        id: uuid,
                        rdnsType: type,
                        geoData: {
                            type: ModuleType.Point,
                            radius: getMetersPerPixel(props.map, props.map.getCenter().lat()) * 30,
                        },
                        injected: false,
                        textInfo: "",
                        label: "",
                    });
                    props.setActiveDialog(null);
                    break;
                case RdnsType.Station:
                    props.addGeoInfos(uuid, {
                        id: uuid,
                        rdnsType: type,
                        geoData: {
                            type: ModuleType.MultiPolygon,
                            points: [],
                        },
                        injected: false,
                        textInfo: "",
                        label: "",
                    });
                    props.setActiveDialog(null);
                    break;
                case RdnsType.Country:
                    props.setActiveDialog(Dialogs.CountrySelector);
                    break;
            }
        } else {
            props.setActiveDialog(null);
        }
    };

    return (
        <DialogBase
            title="What kind of geographic data?"
            data={[
                RdnsType.Headquarters,
                RdnsType.Station,
                RdnsType.Channel,
                RdnsType.Country,
            ]}
            open={props.open}
            getDataKey={getDataKey}
            renderData={renderData}
            onClose={handleOnClose}
        />
    );
};

export const TypeSelector = connect(
    (state: RootReducerState) => ({
        map: state.map.map,
    }),
    (dispatch) => ({
        addGeoInfos: (uuid: string, geoInfo: GeographicInfo) => dispatch(addGeoInfos(uuid, geoInfo)),
        deleteGeoInfos: (uuid: string) => dispatch(deleteGeoInfos(uuid)),
        setActiveDialog: (activeDialog: Dialogs | null) => dispatch(setActiveDialog(activeDialog)),
        setCurrentlyEdited: (currentlyEditedUuid: string) => dispatch(setCurrentlyEdited(currentlyEditedUuid)),
    }),
)(TypeSelectorContainer);