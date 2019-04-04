import {MapPickerModule, MapPickerModuleOpts} from "./MapPickerModule";
import blueDot from "./marker-icons/blue-dot.png"

export interface MarkerModuleOpts extends MapPickerModuleOpts {
    position?: google.maps.LatLngLiteral | google.maps.LatLng,
    circleRadius?: number,
    updateGeoInfosPoint: (uuid: string, center: google.maps.LatLngLiteral, radius: number) => void;
}

export class MarkerModule extends MapPickerModule<MarkerModuleOpts> {
    private circle: google.maps.Circle | null = null;
    private circleEventListener: google.maps.MapsEventListener | null = null;
    private activeEventListener: google.maps.MapsEventListener | null = null;
    private marker: google.maps.Marker | null = null;

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
            this.circle.set("fillColor", "#FF0000");
            this.circle.set("strokeColor", "#FF0000");
            this.circle.setEditable(true);
        }
    };

    public onEditingStopped = () => {
        super.onEditingStopped();
        if (this.marker) {
            this.marker.set("icon", blueDot);
        }

        if (this.circle) {
            this.circle.set("strokeColor", "#9E9E9E");
            this.circle.set("fillColor", "#9E9E9E");
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

    public getItem() {
        return this.item;
    }

    public returnCenter(): google.maps.LatLngLiteral | null {
        return this.marker
            ? {lat: this.marker.getPosition().lat(), lng: this.marker.getPosition().lng()}
            : null;
    }

    public enableActiveListener(): void {
        if (this.circle) {
            this.activeEventListener = this.circle.addListener("click", this.opts.setActive);
        }
    }

    public disableActiveListener(): void {
        if (this.activeEventListener) {
            this.activeEventListener.remove();
        }
    }

    public update(): void {
        if (!this.marker) {
            return;
        }

        this.opts.updateGeoInfosPoint(
            this.opts.uuid,
            {
                lat: this.marker.getPosition().lat(),
                lng: this.marker.getPosition().lng(),
            },
            this.circle ? this.circle.getRadius() : 0,
        );
    }

    protected spawnItem(latLng: google.maps.LatLngLiteral): google.maps.Marker {
        const {map, position, setActive, circleRadius} = this.opts;
        const marker = this.spawnMarker(map, position || latLng, setActive);
        this.spawnCircle(marker, map, position || latLng, circleRadius, setActive);
        return marker;
    }

    private spawnMarker = (map: google.maps.Map | undefined, position: google.maps.LatLngLiteral | google.maps.LatLng, setActive: () => void) => {
        const item = new google.maps.Marker({
            position,
            map,
            draggable: this.opts.draggable,
        });
        item.addListener("click", setActive);
        this.marker = item;
        return item;
    };

    private spawnCircle = (marker: google.maps.Marker, map: google.maps.Map | undefined,
                           center: google.maps.LatLngLiteral | google.maps.LatLng, radius: number | undefined, setActive: () => void) => {
        if (!radius || !marker) {
            return;
        }
        this.circle = new google.maps.Circle({
            strokeColor: "#FF0000",
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: "#FF0000",
            fillOpacity: 0.35,
            map,
            center: marker.getPosition(),
            radius,
            editable: true,
            draggable: false,
        });
        this.activeEventListener = this.circle.addListener("click", setActive);
    };
}
