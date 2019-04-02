import AppBar from '@material-ui/core/AppBar';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import {createStyles, withStyles, WithStyles} from '@material-ui/core/styles';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import MenuIcon from '@material-ui/icons/Menu';
import React from 'react';
import {download} from "../utilities";
import {connect} from "react-redux";
import {RootReducerState} from "../reducers/root-reducer";
import {addGeoInfosBulk, GeographicInfo, setCurrentlyEdited} from "../reducers/map-reducer";
import {GEOJson, importFromGeoJson, saveToGeoJson} from "../geolocation/GEOJson";
import {FileOpener} from "./utilities-components/FileOpener";

const styles = createStyles({
    root: {
        flexGrow: 1,
    },
    grow: {
        flexGrow: 1,
    },
    menuButton: {
        marginLeft: -12,
        marginRight: 20,
    },
});

export interface Props extends WithStyles<typeof styles> {
    // injected
    geoInfos?: { [uuid: string]: GeographicInfo };
    map?: google.maps.Map | null;

    addGeoInfosBulk?:  (geoInfos: {[uuid: string]: GeographicInfo}) => void;
    setCurrentlyEdited?: (currentlyEditedUuid: string) => () => void;
}

class ButtonAppBarUnstyled extends React.Component<Props> {
    private inputRef: HTMLInputElement | null = null;

    public render() {
        const {classes} = this.props;

        return (
            <div className={classes.root}>
                <FileOpener
                    onFiles={this.handleOnFiles}
                    setInputRef={this.setInputRef}
                />
                <AppBar position="static">
                    <Toolbar>
                        <IconButton className={classes.menuButton} color="inherit" aria-label="Menu">
                            <MenuIcon/>
                        </IconButton>
                        <Typography variant="h6" color="inherit" className={classes.grow}>
                            Polygons picker
                        </Typography>
                        <Button color="inherit" onClick={this.onClickImport}>Import GeoJson</Button>
                        <Button color="inherit" onClick={this.onClickExport}>Export to GeoJson</Button>
                    </Toolbar>
                </AppBar>
            </div>
        )
    }

    private setInputRef = (ref: HTMLInputElement | null) => this.inputRef = ref;

    private onClickExport = () => download("polygons.geojson", JSON.stringify(saveToGeoJson(this.props.geoInfos!)));

    private onClickImport = () => {
        if (this.inputRef) {
            this.inputRef.click()
        }
    };

    private handleOnFiles = async (files: FileList | null) => {
        if (!files) {
            return;
        }
        await Promise.all(Array.from(files).map(async (file) => {
            const reader = new FileReader();
            const promise = new Promise<string | ArrayBuffer | null>((res) => {
                reader.onload = () => res(reader.result)
            });
            reader.readAsText(file);
            const result: string | ArrayBuffer | null = await promise;

            if (typeof result !== "string") {
                return;
            }
            const parsed: GEOJson = JSON.parse(result);
            const parsedGeoResult = importFromGeoJson(parsed, this.props.map!, this.props.setCurrentlyEdited!, () => {});

            if (parsedGeoResult.geographicInfos) {
                this.props.addGeoInfosBulk!(parsedGeoResult.geographicInfos);
            }
        }));
        this.props.setCurrentlyEdited!("")();
    }
}

export const ButtonAppBar = connect(
    (state: RootReducerState) => ({
        geoInfos: state.map.geoInfos,
        map: state.map.map,
    }),
    (dispatch) => ({
        addGeoInfosBulk: (geoInfos: {[uuid: string]: GeographicInfo}) => dispatch(addGeoInfosBulk(geoInfos)),
        setCurrentlyEdited: (currentlyEditedUuid: string) => () => dispatch(setCurrentlyEdited(currentlyEditedUuid)),
    })
)(withStyles(styles)(ButtonAppBarUnstyled));