import {ListItemAvatar} from "@material-ui/core";
import Avatar from "@material-ui/core/es/Avatar";
import ListItemText from "@material-ui/core/es/ListItemText";
import {Home, Radio, RssFeed} from "@material-ui/icons";
import * as React from "react";
import {DialogSelector} from "../DialogSelector";
import {MapPickerModuleType, mapPickerTypeToIconAndText} from "./MapPickerModule";

interface Props {
    onClose: (data: MapPickerModuleType | null) => void;
    open: boolean;
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

export const MapPickerTypeSelector: React.FunctionComponent<Props> = (props) => (
    <DialogSelector
        title="What kind of geographic data?"
        data={[
            MapPickerModuleType.Headquarters,
            MapPickerModuleType.Station,
            MapPickerModuleType.Channel,
        ]}
        open={props.open}
        getDataKey={getDataKey}
        renderData={renderData}
        onClose={props.onClose}
    />
);
