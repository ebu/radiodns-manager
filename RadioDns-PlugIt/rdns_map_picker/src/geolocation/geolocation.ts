export const getCurrentPosition: () => Promise<google.maps.LatLngLiteral> = () => {
    return new Promise(async (res) => {
        if (!("geolocation" in navigator) || !(await handlePermission())) {
            res({lat: 46.948927005132, lng: 7.4074140555507});
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (position) => res({lat: position.coords.latitude, lng: position.coords.longitude}),
            (err) => {
                console.warn(err);
                res({lat: 46.948927005132, lng: 7.4074140555507});
            },
        );
    });
};

export const handlePermission: () => Promise<boolean> = () => {
    return new Promise((res) => {
        (navigator as any).permissions.query({name: 'geolocation'}).then((result: any) => {
            res(result.state == 'granted' || result.state == 'prompt');
        });
    })
};
