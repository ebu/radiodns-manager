import { saveAs } from "file-saver";

export const download = (filename: string, text: string) => {
    saveAs(new Blob([text], {type: "text/plain;charset=utf-8"}), filename);
};

// tslint:disable no-object-literal-type-assertion
export const objectWithoutProperties = <T extends object>(obj: T, keys: Array<keyof T>) => {
    const target: T = ({} as T);
    for (const prop in obj) {
        if (obj.hasOwnProperty(prop) && !keys.includes(prop)) {
            target[prop] = obj[prop];
        }
    }
    return target;
};
// tslint:enable

// tslint:disable
// @ts-ignore
export const uuidv4 = () => ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16),
);
// tslint:enable
