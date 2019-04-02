export const getCurrentPosition: () => Promise<google.maps.LatLngLiteral> = () => {
    return new Promise(async (res) => res({lat: 46.948927005132, lng: 7.4074140555507}));
};

export const handlePermission: () => Promise<boolean> = () => {
    return new Promise((res) => {
        (navigator as any).permissions.query({name: 'geolocation'}).then((result: any) => {
            res(result.state == 'granted' || result.state == 'prompt');
        });
    })
};
