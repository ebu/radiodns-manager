import {Home, Radio, RssFeed} from "@material-ui/icons";
import * as React from "react";

export enum MapPickerModuleType {
    Headquarters = "Headquarters",
    Station = "Station",
    Channel = "Channel",
}

export const mapPickerTypeToIconAndText = (data: MapPickerModuleType) => {
    let icon = <Home/>;
    let text = "Headquarters";

    switch (data) {
        case MapPickerModuleType.Station:
            icon = <Radio/>;
            text = "Station";
            break;
        case MapPickerModuleType.Channel:
            icon = <RssFeed/>;
            text = "Channel";
            break;
    }
    return {icon, text};
};


export interface MapPickerModule {
    init: (map: google.maps.Map) => void;
    onStartEdit: () => void;
    onEditingStopped: () => void;
    returnPoints: () => google.maps.LatLngLiteral[];
}
