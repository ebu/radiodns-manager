import {MapPickerModule} from "./MapPickerModule";

export class PolygonModule implements MapPickerModule {
    private eventListener: google.maps.MapsEventListener| null = null;
    private polygon: google.maps.Polygon | null = null;

    public init(map: google.maps.Map) {
        const evtListener = map.addListener("click", (e) => {
            const latLng = {lat: e.latLng.lat(), lng: e.latLng.lng()};
            if (this.polygon) {
                this.polygon.setMap(null);
            }
            const polygon = new google.maps.Polygon({
                paths: [
                    new google.maps.LatLng(latLng.lat, latLng.lng),
                    new google.maps.LatLng(latLng.lat - 1, latLng.lng),
                    new google.maps.LatLng(latLng.lat, latLng.lng + 1),
                ],
                geodesic: false,
                strokeOpacity: 0.8,
                strokeWeight: 2,
                fillOpacity: 0.35,
                strokeColor: '#FF0000',
                fillColor: '#FF0000',
                editable: true,
                draggable: true,
            });
            this.eventListener = polygon.addListener("rightclick", this.handleRightClick);
            polygon.setMap(map);
            evtListener.remove();
            this.polygon = polygon;
        });
        return this;
    };

    public onStartEdit(): void {
        if (this.polygon) {
            this.eventListener = this.polygon.addListener("rightclick", this.handleRightClick);
            this.polygon.set("strokeColor", '#FF0000');
            this.polygon.set("fillColor", '#FF0000');
            this.polygon.setEditable(true);
            this.polygon.setDraggable(true);
        }
    }

    public onEditingStopped(): void {
        if (this.eventListener && this.polygon) {
            this.eventListener.remove();
            this.polygon.set("strokeColor", '#9E9E9E');
            this.polygon.set("fillColor", '#9E9E9E');
            this.polygon.setEditable(false);
            this.polygon.setDraggable(false);
        }
    }

    public returnPoints(): google.maps.LatLngLiteral[] {
        return this.polygon
            ? this.polygon.getPath().getArray().map((latLng) => latLng.toJSON())
            : [];
    }

    private handleRightClick = (e: any) => {
        if (e.vertex == undefined) {
            return;
        }
    }
}
