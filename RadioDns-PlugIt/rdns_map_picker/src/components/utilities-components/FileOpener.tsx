import * as React from "react";

interface Props {
    multiple?: boolean;
    onFiles: (files: FileList | null) => void;
    setInputRef: (ref: HTMLInputElement | null) => void
}

export const FileOpener: React.FunctionComponent<Props> = (props) => {
    const handleOnChange = (e: React.ChangeEvent<HTMLInputElement>) => props.onFiles(e.target.files);
    return (
            <input
                multiple={props.multiple}
                ref={props.setInputRef}
                style={{display: "none"}}
                type="file"
                accept=".geojson,.json"
                onChange={handleOnChange}
            />
        );
};
