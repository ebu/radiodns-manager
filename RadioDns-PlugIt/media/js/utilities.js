function UtilitiesModule() {
}

/**
 * Retrieve a javascript accessible cookie's value.
 * @param name: the name of the cookie (its key).
 * @returns the value if the cookie was found or null.
 */
UtilitiesModule.prototype.getCookie = function (name) {
    const parts = ("; " + document.cookie).split("; " + name + "=");
    if (parts.length === 2) {
        return parts.pop().split(";").shift()
    }
    return null;
};

/**
 * Make an ajax request. Automatic conversion from json to javascript object and vis versa.
 *
 * Note: Currently the PlugIt api does not allow any other status code than 200 when generating json response.
 * So that is why the status code are included in the response.
 *
 * @param url: The url of the requested resource.
 * @param method: The method of the request (GET, POST, DELETE, PATCH, PUT).
 * @param data: The payload.
 * @returns A promise of result.
 */
UtilitiesModule.prototype.request = function (url, method, data = undefined) {
    return axios({
        url,
        method,
        data,
        transformRequest: [function (data) {
            if (method !== "GET") {
                return JSON.stringify(data);
            }
        }],
        transformResponse: [function (data) {
            if (method !== "GET") {
                return JSON.parse(data);
            }
        }],
        headers: {
            "X-CSRFToken": UtilitiesModule.prototype.getCookie("csrftoken"),
        },
    })
        .then(function (response) {
            if (response.data && response.data.error) {
                return Promise.reject({status: response.data.status, msg: response.data.error})
            }
            return response.data;
        })
};

/**
 * Return true if both array have the same elements, not necessarily in the same order.
 * @param arr1: The first array.
 * @param arr2: The second array.
 * @returns {boolean}
 */
UtilitiesModule.prototype.arrayEquals = function (arr1, arr2) {
    if (arr2.length !== arr1.length) {
        return false;
    }
    return arr1
        .reduce(function (acc, elem) {
            acc.push(arr2.includes(elem));
            return acc;
        }, [])
        .every(function (elem) {
            return elem;
        })
};
