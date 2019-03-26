import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import * as React from 'react';

interface Props<T> {
    title: string;
    onClose: (selected: T | null) => void;
    data: T[];
    getDataKey: (data: T) => string;
    renderData: (data: T) => React.ReactNode;
    open: boolean;
}

export const DialogSelector = <T extends any>(props: Props<T>) => {
    const { open, onClose, data, getDataKey, renderData, ...other } = props;

    function handleClose() {
        onClose(null);
    }

    function handleListItemClick(value: T) {
        onClose(value);
    }

    return (
        <Dialog open={open} onClose={handleClose} aria-labelledby="simple-dialog-title" {...other}>
            <DialogTitle id="simple-dialog-title">{props.title}</DialogTitle>
            <div>
                <List>
                    {data.map((data) => (
                        <ListItem button onClick={() => handleListItemClick(data)} key={getDataKey(data)}>
                            {renderData(data)}
                        </ListItem>
                    ))}
                </List>
            </div>
        </Dialog>
    );
};
