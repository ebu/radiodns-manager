import {ListItemAvatar} from "@material-ui/core";
import Avatar from "@material-ui/core/es/Avatar";
import ListItemText from "@material-ui/core/es/ListItemText";
import * as React from "react";
import {connect} from "react-redux";
import {Dialogs, setActiveDialog} from "../../../reducers/dialog-reducer";
import {addGeoInfos, deleteGeoInfos, GeographicInfo, setCurrentlyEdited} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";
import {uuidv4} from "../../../utilities";
import {MapPickerModuleType, mapPickerTypeToIconAndText} from "../modules/MapPickerModule";
import {MarkerModule} from "../modules/MarkerModule";
import {PolygonModule} from "../modules/PolygonModule";
import {getMetersPerPixel} from "../utilities";
import {DialogBase} from "./DialogBase";

interface Props {
    open: boolean;

    // injected
    map?: google.maps.Map | null;
    addGeoInfos?: (uuid: string, geoInfo: GeographicInfo) => void;
    deleteGeoInfos?: (uuid: string) => void;
    setActiveDialog?: (activeDialog: Dialogs | null) => void;
    setCurrentlyEdited?: (currentlyEditedUuid: string) =>  void;
}

const getDataKey = (data: MapPickerModuleType) => data;

const renderData = (data: MapPickerModuleType) => {
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

    const handleOnClose = (type: MapPickerModuleType | null) => {
        if (type && props.map) {
            const uuid = uuidv4();

            switch (type) {
                case MapPickerModuleType.Headquarters:
                case MapPickerModuleType.Channel:
                    props.addGeoInfos!(uuid, {
                        id: uuid,
                        type,
                        module: new MarkerModule({
                            map: props.map,
                            circleRadius: type === MapPickerModuleType.Channel
                                ? getMetersPerPixel(props.map, props.map.getCenter().lat()) * 30
                                : undefined,
                            setActive: () => props.setCurrentlyEdited!(uuid),
                            draggable: true,
                            editable: true,
                            openDeleteMenu: () => {},
                            noClick: false,
                        }),
                    });
                    props.setActiveDialog!(null);
                    break;
                case MapPickerModuleType.Station:
                    props.addGeoInfos!(uuid, {
                        id: uuid,
                        type,
                        module: new PolygonModule({
                            map: props.map,
                            editable: true,
                            draggable: true,
                            setActive: () => props.setCurrentlyEdited!(uuid),
                            openDeleteMenu: () => {},
                            noClick: false,
                        }),
                    });
                    props.setActiveDialog!(null);
                    break;
                case MapPickerModuleType.Country:
                    props.setActiveDialog!(Dialogs.CountrySelector);
                    break;
            }
        } else {
            props.setActiveDialog!(null);
        }
    };

    return (
        <DialogBase
            title="What kind of geographic data?"
            data={[
                MapPickerModuleType.Headquarters,
                MapPickerModuleType.Station,
                MapPickerModuleType.Channel,
                MapPickerModuleType.Country,
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
    })
)(TypeSelectorContainer);
