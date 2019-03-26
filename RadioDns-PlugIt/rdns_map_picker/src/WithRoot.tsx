import {green} from "@material-ui/core/colors";
import CssBaseline from '@material-ui/core/CssBaseline';
import {deepPurple, indigo} from "@material-ui/core/es/colors";
import {createMuiTheme, MuiThemeProvider} from '@material-ui/core/styles';
import * as React from 'react';
import {ButtonAppBar} from "./components/ApplicationBar";

// A theme with custom primary and secondary color.
// It's optional.
const theme = createMuiTheme({
    palette: {
        primary: indigo,
        secondary: deepPurple,
    },
    typography: {
        useNextVariants: true,
    },
});

function withRoot<P>(Component: React.ComponentType<P>) {
    function WithRoot(props: P) {
        // MuiThemeProvider makes the theme available down the React tree
        // thanks to React context.
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
