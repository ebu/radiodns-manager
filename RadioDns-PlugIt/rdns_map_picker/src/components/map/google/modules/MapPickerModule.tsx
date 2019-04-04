import {Home, Radio, RssFeed, Terrain} from "@material-ui/icons";
import * as React from "react";
import {RdnsType} from "../../../../reducers/map-reducer";

export const mapPickerTypeToIconAndText = (data: RdnsType) => {
    let icon = <Home/>;
    let text = "Headquarters";

    switch (data) {
        case RdnsType.Station:
            icon = <Radio/>;
            text = "Station";
            break;
        case RdnsType.Channel:
            icon = <RssFeed/>;
            text = "Channel";
            break;
        case RdnsType.Country:
            icon = <Terrain/>;
            text = "Country";
            break;
    }
    return {icon, text};
};

export interface MapPickerModuleOpts {
    uuid: string;
    map: google.maps.Map;
    editable: boolean;
    draggable: boolean;
    noClick: boolean;
    label?: string;
    textInfo?: string;
    setActive: () => void;
}

type ModuleType = google.maps.Marker | google.maps.Polygon;

export abstract class MapPickerModule<T extends MapPickerModuleOpts> {
    protected item: ModuleType | null = null;
    protected opts: T;
    private evtListener: google.maps.MapsEventListener | null = null;

    constructor(opts: T) {
        this.opts = opts;
    }

    public init() {
        const {map, noClick, setActive} = this.opts;

        if (noClick) {
            this.item = this.spawnItem();
            this.onEditingStopped();
        } else if (map) {
            const evtListener = map.addListener("click", (e) => {
                const latLng = {lat: e.latLng.lat(), lng: e.latLng.lng()};
                this.item = this.spawnItem(latLng);
                evtListener.remove();
                this.onStartEdit();
            });
            setActive();
        } else {
            throw new Error("Map object creation failed: No default map was provided for the selected spawn rdnsType: \"Click\".");
        }
        return this;
    }

    public onStartEdit(): void {
        if (this.item) {
            this.item.set("strokeColor", "#FF0000");
            this.item.set("fillColor", "#FF0000");
            this.item.set("editable", this.opts.editable);
            this.item.set("draggable", this.opts.draggable);
            if (this.opts.draggable && this.evtListener === null) {
                this.evtListener = this.item.addListener("dragend", () => this.update())
            }
        }
        this.updateItemZIndex(1000);
    }

    public onEditingStopped(): void {
        if (this.item) {
            this.item.set("strokeColor", "#9E9E9E");
            this.item.set("fillColor", "#9E9E9E");
            this.item.set("editable", false);
            this.item.set("draggable", false);
        }
        this.updateItemZIndex(100);
    }

    public onDelete() {
        if (this.item) {
            this.item.setMap(null);
        }
    };

    public setMap(map: google.maps.Map) {
        if (this.item) {
            this.item.setMap(map);
        }
    }

    public getOptions() {
        return this.opts;
    }

    public getItem() {
        return this.item;
    }

    public abstract update(): void;

    public abstract returnPoints(): google.maps.LatLngLiteral[][];

    public abstract returnCenter(): google.maps.LatLngLiteral | null;

    public abstract enableActiveListener(): void;

    public abstract disableActiveListener(): void;

    protected abstract spawnItem(latLng?: google.maps.LatLngLiteral): ModuleType;

    private updateItemZIndex(zIndex: number) {
        if (this.item) {
            this.item.set("zIndex", zIndex);
        }
    }

}
