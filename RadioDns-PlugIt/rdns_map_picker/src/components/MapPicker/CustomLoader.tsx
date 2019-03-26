import * as React from "react";
import {LoadScript} from "@react-google-maps/api";

export class CustomLoader extends LoadScript {
    public render(): JSX.Element {
        return (
            <div ref={this.check} style={{width: "100%", height: "100%"}}>
                {this.state.loaded ? this.props.children : this.props.loadingElement}
            </div>
        )
    }
}
