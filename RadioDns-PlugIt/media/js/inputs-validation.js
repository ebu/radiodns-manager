function InputsValidation() {
}


/**
 * Checks an input's validity against a set of rules. Calls onInvalidValue if the submitted value does not comply
 * to one rule. Otherwise calls onValidValue.
 * @param value: The value to be verified.
 * @param rules: The rules that will verify the value. A rule has the shape: (value: string) => {isValid: boolean, errorMsg: string}
 * @param onInvalidValue: Callback that takes an error message as an argument. Fires when a value failed to comply to a rule.
 * @param onValidValue: Callback that fires when a value complies to all the specified rules.
 * @returns {boolean}: True if the value is valid, false otherwise.
 */
InputsValidation.prototype.checkInputValidity = function (value, rules, onInvalidValue, onValidValue) {
    for (let i = 0; i < rules.length; i++) {
        const res = rules[i](value);
        if (!res.isValid) {
            onInvalidValue(res.errorMsg);
            return false;
        }
    }
    onValidValue();
    return true;
};

/**
 * Rule factory. Checks if the input is not empty.
 * @param inputName: The name of the input.
 * @returns {function(*): {isValid: boolean, errorMsg: string}}
 */
InputsValidation.prototype.inputCannotBeEmpty = function (inputName) {
    return function (value) {
        return {
            isValid: value.length !== 0,
            errorMsg: `The ${inputName} cannot be empty.`,
        };
    };
};

/**
 * Rule factory. Checks if the input is no longer than the specified max length.
 * @param inputName: The name of the input.
 * @param maxLength: The maximum length the input can have.
 * @returns {function(*): {isValid: boolean, errorMsg: string}}
 */
InputsValidation.prototype.inputCannotBeLongerThan = function(inputName, maxLength) {
    return function (value) {
        return {
            isValid: value.length <= maxLength,
            errorMsg: `The ${inputName} cannot be longer than ${maxLength} characters.`,
        };
    };
};

/**
 * Rule factory. Checks if the input is at least longer than the specified min length.
 * @param inputName: The name of the input.
 * @param minLength: The minimum length the input must have.
 * @returns {function(*): {isValid: boolean, errorMsg: string}}
 */
InputsValidation.prototype.inputCannotBeShorterThan = function(inputName, minLength) {
    return function (value) {
        return {
            isValid: value.length >= minLength,
            errorMsg: `The ${inputName} cannot be shorter than ${minLength} characters.`,
        };
    };
};

/**
 * Rule factory. Check if the input contains only alphanumerics. [a-zA-Z0-9]
 * @param inputName: The name of the input.
 * @returns {function(*=): {isValid: boolean, errorMsg: string}}
 */
InputsValidation.prototype.onlyAlphanumeric = function (inputName) {
    return function (value) {
        return {
            isValid: /^[a-zA-Z0-9]*$/.test(value),
            errorMsg: `The ${inputName} can only contain letters and numbers.`,
        };
    }
};

/**
 * Checks if an email is valid. If it is, returns true, false otherwise.
 * @param email: The email.
 * @returns {{isValid: boolean, errorMsg: string}}
 */
InputsValidation.prototype.emailValid = function (email) {
    return {
        isValid: /^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$/.test(email),
        errorMsg: "Invalid email.",
    };
};
