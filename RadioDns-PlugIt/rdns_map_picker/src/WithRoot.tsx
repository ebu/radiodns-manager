import CssBaseline from "@material-ui/core/CssBaseline";
import {indigo, pink} from "@material-ui/core/es/colors";
import {createMuiTheme, MuiThemeProvider} from "@material-ui/core/styles";
import * as React from "react";
import {ButtonAppBar} from "./components/ApplicationBar";

// A theme with custom primary and secondary color.
// It's optional.
const theme = createMuiTheme({
    palette: {
        primary: indigo,
        secondary: pink,
    },
    typography: {
        useNextVariants: true,
    },
});

function withRoot<P>(Component: React.ComponentType<P>) {
    function WithRoot(props: P) {
        return (
            <MuiThemeProvider theme={theme}>
                {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
                <CssBaseline />
                <ButtonAppBar/>
                <Component {...props} />
            </MuiThemeProvider>
        );
    }

    return WithRoot;
}

export default withRoot;
