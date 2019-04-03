import {MapPickerModule, MapPickerModuleOpts} from "./MapPickerModule";

export interface PolygonModuleOpts extends MapPickerModuleOpts {
    paths?: google.maps.LatLngLiteral[] | google.maps.LatLngLiteral[][]
}

export class PolygonModule extends MapPickerModule<PolygonModuleOpts> {
    private clickEvtListener: google.maps.MapsEventListener | null = null;

    public returnPoints(): google.maps.LatLngLiteral[][] {
        return this.item ? (this.item as google.maps.Polygon).getPaths().getArray()
                .map((polygon) => polygon.getArray().map((point) => ({lat: point.lat(), lng: point.lng()})))
            : [];
    }

    protected spawnItem(latLng?: google.maps.LatLngLiteral): google.maps.Polygon {
        const {map, editable, draggable, paths, setActive, noClick} = this.opts;
        const gmarker = this.item as google.maps.Polygon | null;

        if (gmarker) {
            gmarker.setMap(null);
        }
        const polygon = new google.maps.Polygon({
            paths: noClick ? paths : [
                new google.maps.LatLng(latLng!.lat, latLng!.lng),
                new google.maps.LatLng(latLng!.lat - 1, latLng!.lng),
                new google.maps.LatLng(latLng!.lat, latLng!.lng + 1),
            ],
            geodesic: true,
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillOpacity: 0.35,
            strokeColor: '#FF0000',
            fillColor: '#FF0000',
            editable,
            draggable,
            map,
        });
        this.clickEvtListener = polygon.addListener("click", setActive);
        return polygon;
    }

    public returnCenter(): google.maps.LatLngLiteral | null {
        if (!this.item) {
            return null;
        }

        const bounds = new google.maps.LatLngBounds();

        this.returnPoints().flatMap((polygon) => polygon)
            .forEach((point) => bounds.extend(point));

        return {lat: bounds.getCenter().lat(), lng: bounds.getCenter().lng()};
    }

    public enableActiveListener(): void {
        if (this.item) {
            this.clickEvtListener = this.item.addListener("click", this.opts.setActive);
        }
    }

    public disableActiveListener(): void {
        if (this.clickEvtListener) {
            this.clickEvtListener.remove();
        }
    }
}
