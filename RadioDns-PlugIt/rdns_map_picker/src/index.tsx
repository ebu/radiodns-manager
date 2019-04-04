import React from "react";
import ReactDOM from "react-dom";
import {Provider} from "react-redux";
import {MapPicker} from "./components/MapPicker/MapPicker";
import {store} from "./reducers/root-reducer";

ReactDOM.render((
    <Provider store={store}>
        <MapPicker/>
    </Provider>
), document.getElementById("root"));
