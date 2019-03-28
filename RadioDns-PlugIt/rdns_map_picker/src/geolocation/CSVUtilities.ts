import {GeographicInfo} from "../reducers/map-reducer";

export const saveToCSV = (geoInfos: { [uuid: string]: GeographicInfo }) =>
    Object.values(geoInfos).map((geoInfo) => `${geoInfo.type},${geoInfo.module},${geoInfo.module.returnPoints()}`);
