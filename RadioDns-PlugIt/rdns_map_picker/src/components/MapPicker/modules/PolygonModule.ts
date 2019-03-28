import {MapPickerModule, MapPickerModuleOpts} from "./MapPickerModule";

export interface PolygonModuleOpts extends MapPickerModuleOpts {
    paths?: google.maps.LatLngLiteral[] | google.maps.LatLngLiteral[][]
    openDeleteMenu: () => void;
    setActive: () => void,
}

export class PolygonModule extends MapPickerModule<PolygonModuleOpts> {
    private polygon: google.maps.Polygon | null = null;

    public returnPoints(): google.maps.LatLngLiteral[][]  {
        return this.polygon
            ? this.polygon.getPaths().getArray()
                .map((polygon) => polygon.getArray().map((point) => ({lat: point.lat(), lng: point.lng()})))
            : [];
    }

    protected spawnItem(latLng?: google.maps.LatLngLiteral): google.maps.Polygon | google.maps.Marker {
        const {map, editable, draggable, paths, setActive, noClick} = this.opts;

        if (this.polygon) {
            this.polygon.setMap(null);
        }
        const polygon = new google.maps.Polygon({
            paths: noClick ? paths : [
                new google.maps.LatLng(latLng!.lat, latLng!.lng),
                new google.maps.LatLng(latLng!.lat - 1, latLng!.lng),
                new google.maps.LatLng(latLng!.lat, latLng!.lng + 1),
            ],
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillOpacity: 0.35,
            strokeColor: '#FF0000',
            fillColor: '#FF0000',
            editable,
            draggable,
            map,
        });
        polygon.addListener("click", setActive);
        return polygon;
    }
}
