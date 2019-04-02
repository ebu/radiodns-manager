import {MapPickerModule, MapPickerModuleOpts} from "./MapPickerModule";
import blueDot from "./marker-icons/blue-dot.png"

export interface MarkerModuleOpts extends MapPickerModuleOpts {
    position?: google.maps.LatLngLiteral | google.maps.LatLng,
    circleRadius?: number,
}

export class MarkerModule extends MapPickerModule<MarkerModuleOpts> {
    private marker: google.maps.Marker | null = null;
    private circle: google.maps.Circle | null = null;
    private circleEventListener: google.maps.MapsEventListener | null = null;

    public onStartEdit = () => {
        super.onStartEdit();
        if (this.marker) {
            this.marker.set("icon", undefined);
            this.circleEventListener = this.marker.addListener("drag", (e) => {
                if (this.circle) {
                    this.circle.set("center", e.latLng)
                }
            });
        }

        if (this.circle) {
            this.circle.set("fillColor", '#FF0000');
            this.circle.set("strokeColor", '#FF0000');
            this.circle.setEditable(true);
        }
    };

    public onEditingStopped = () => {
        super.onEditingStopped();
        if (this.marker) {
            this.marker.set("icon", blueDot);
        }

        if (this.circle) {
            this.circle.set("strokeColor", '#9E9E9E');
            this.circle.set("fillColor", '#9E9E9E');
            this.circle.setEditable(false);
        }

        if (this.circleEventListener) {
            this.circleEventListener.remove();
        }
    };

    public returnPoints = () => this.marker
        ? [[{lat: this.marker.getPosition().lat(), lng: this.marker.getPosition().lng()}]]
        : [[]];

    public onDelete(): void {
        super.onDelete();
        if (this.circle) {
            this.circle.setMap(null);
        }
    }

    public setMap(map: google.maps.Map) {
        super.setMap(map);
        if (this.circle) {
            this.circle.setMap(map);
        }
    }

    public getCircleRadius() {
        if (this.circle) {
            return this.circle.getRadius();
        }
        return 0;
    }

    protected spawnItem(latLng: google.maps.LatLngLiteral): google.maps.Polygon | google.maps.Marker {
        const {map, position, setActive, circleRadius} = this.opts;
        this.spawnMarker(map, position || latLng, setActive);
        this.spawnCircle(map, position || latLng, circleRadius, setActive);
        return this.marker!;
    }

    private spawnMarker = (map: google.maps.Map | undefined, position: google.maps.LatLngLiteral | google.maps.LatLng, setActive: () => void) => {
        this.marker = new google.maps.Marker({
            position,
            map,
            draggable: true,
        });
        this.marker.addListener("click", setActive);
    };

    private spawnCircle = (map: google.maps.Map | undefined, center: google.maps.LatLngLiteral | google.maps.LatLng, radius: number | undefined, setActive: () => void) => {
        if (!radius || !this.marker) {
            return;
        }
        this.circle = new google.maps.Circle({
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35,
            map,
            center: this.marker.getPosition(),
            radius,
            editable: true,
            draggable: false,
        });
        this.circle.addListener("click", setActive);
    }
}
