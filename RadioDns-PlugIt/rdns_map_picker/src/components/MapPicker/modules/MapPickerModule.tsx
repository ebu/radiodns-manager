import {Home, Radio, RssFeed, Terrain} from "@material-ui/icons";
import * as React from "react";

export enum MapPickerModuleType {
    Headquarters = "Headquarters",
    Station = "Station",
    Channel = "Channel",
    Country = "Country",
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
        case MapPickerModuleType.Country:
            icon = <Terrain/>;
            text = "Country";
            break;
    }
    return {icon, text};
};


export interface MapPickerModuleOpts {
    map: google.maps.Map;
    editable: boolean;
    draggable: boolean;
    noClick: boolean;
    setActive: () => void;
    openDeleteMenu: () => void;
}

export abstract class MapPickerModule<T extends MapPickerModuleOpts> {
    protected item: google.maps.Polygon | google.maps.Marker | null =  null;
    protected opts: T;

    constructor(opts: T) {
        const {map, noClick} = opts;
        this.opts = opts;

        if (noClick) {
            this.item = this.spawnItem();
            this.onStartEdit();
        } else {
            const evtListener = map.addListener("click", (e) => {
                const latLng = {lat: e.latLng.lat(), lng: e.latLng.lng()};
                this.item = this.spawnItem(latLng);
                evtListener.remove();
                this.onStartEdit();
            });
        }
        opts.setActive();
    }

    public onStartEdit(): void {
        if (this.item) {
            this.item.set("strokeColor", '#FF0000');
            this.item.set("fillColor", '#FF0000');
            this.item.set("editable", this.opts.editable);
            this.item.set("draggable", this.opts.draggable);
        }
    }

    public onEditingStopped(): void {
        if (this.item) {
            this.item.set("strokeColor", '#9E9E9E');
            this.item.set("fillColor", '#9E9E9E');
            this.item.set("editable", false);
            this.item.set("draggable", false);
        }
    }

    public abstract returnPoints(): google.maps.LatLngLiteral[][];

    protected abstract spawnItem(latLng?: google.maps.LatLngLiteral): google.maps.Polygon | google.maps.Marker;
}
