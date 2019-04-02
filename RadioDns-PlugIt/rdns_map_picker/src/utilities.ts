// @ts-ignore
export const uuidv4 = () => ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
);

export const download = (filename: string, text: string) => {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
};

export const objectWithoutProperties = <T extends object>(obj: T, keys: Array<keyof T>) => {
    let target: T = {} as T;
    for (const prop in obj) {
        if (obj.hasOwnProperty(prop) && !keys.includes(prop)) {
            target[prop] = obj[prop];
        }
    }
    return target;
};
