import {TextField} from "@material-ui/core";
import Dialog from "@material-ui/core/Dialog";
import DialogTitle from "@material-ui/core/DialogTitle";
import ListItemText from "@material-ui/core/es/ListItemText";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import withStyles, {StyledComponentProps, StyleRulesCallback} from "@material-ui/core/styles/withStyles";
import * as React from "react";

const styles: StyleRulesCallback<any> = (theme) => ({
    searchField: {
        padding: theme.spacing.unit,
    },
});

interface Props<T> extends StyledComponentProps {
    title: string;
    onClose: (selected: T | null) => void;
    data: T[];
    getDataKey: (data: T) => string;
    renderData: (data: T) => React.ReactNode;
    open: boolean;
    searchFieldTitle?: string;
}

const DialogBaseUnstyled = <T extends any>(props: Props<T>) => {
    const {title, searchFieldTitle, classes, open, onClose, data, getDataKey, renderData, ...other} = props;

    const handleClose = () => {
        onClose(null);
    };

    const [dataFilter, setDataFilter] = React.useState("");

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => setDataFilter(event.target.value);

    const filtered = data.filter((d) => getDataKey(d).toLocaleLowerCase().startsWith(dataFilter.toLocaleLowerCase()));
    return (
        <Dialog open={open} onClose={handleClose} aria-labelledby="simple-dialog-title" {...other}>
            <DialogTitle id="simple-dialog-title">{title}</DialogTitle>
            {searchFieldTitle && <TextField
                id="outlined-name"
                label={searchFieldTitle}
                value={dataFilter}
                onChange={handleChange}
                margin="normal"
                variant="outlined"
                className={classes!.searchField}
            />}
            <div>
                <List>
                    {
                        filtered.map((d) => (
                            <ListItem button onClick={handleClose} key={getDataKey(d)}>
                                {renderData(d)}
                            </ListItem>
                        ))}
                    {filtered.length === 0 && <ListItemText primary="No results."/>}
                </List>
            </div>
        </Dialog>
    );
};

export const DialogBase = withStyles(styles)(DialogBaseUnstyled);
