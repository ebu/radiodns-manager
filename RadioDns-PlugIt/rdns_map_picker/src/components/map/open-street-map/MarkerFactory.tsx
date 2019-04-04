import * as React from "react";
import {Circle, Marker, Polygon, Popup} from "react-leaflet";
import {connect} from "react-redux";
import {GeographicInfo, ModuleType} from "../../../reducers/map-reducer";
import {RootReducerState} from "../../../reducers/root-reducer";

interface Props {
    geoInfo: GeographicInfo;
}

class MarkerFactoryContainer extends React.Component<Props> {

    public render() {
        const geoData = this.props.geoInfo.geoData;
        switch (geoData.type) {
            case ModuleType.MultiPolygon:
                return (
                    <Polygon color="purple" positions={geoData.points}>
                        {this.props.geoInfo.label && <Popup>
                            <b>{this.props.geoInfo.label}</b> <br/> {this.props.geoInfo.textInfo}
                        </Popup>}
                    </Polygon>
                );
            default: {
                const center = geoData.center;
                if (!center) {
                    return null;
                }
                return (
                    <>
                        <Marker position={[center.lat, center.lng]} key={this.props.geoInfo.id}>
                            {this.props.geoInfo.label && <Popup>
                                <b>{this.props.geoInfo.label}</b> <br/> {this.props.geoInfo.textInfo}
                            </Popup>}
                        </Marker>
                        {geoData.radius > 0 && <Circle
                            center={[center.lat, center.lng]}
                            radius={geoData.radius}
                            color="purple"
                        />}
                    </>
                );
            }
        }
    }
}

export const MarkerFactory = connect(
    (state: RootReducerState) => ({}),
    (dispatch) => ({}),
)(MarkerFactoryContainer);
