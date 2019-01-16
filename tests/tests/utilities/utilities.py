import re

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def sql_alchemy_result_to_list(result):
    """
    Converts the result of a sqlAlchemy proxy result object into a list of list (list of rows).

    Note: This function consume the sqlAlchemy result so two or more calls on the same sqlAlchemy result will
    result of inconsistencies across the results. For example, if called twice on the same result, the first will
    return the result's row, the second an empty list.

    :param result: the sqlAlchemy query result.
    :return: the converted list.
    """
    result_list = []
    for row in result:
        result_list.append(list(row))

    return result_list


def normalize_list(string_list):
    """
    Normalizes the contents of a list of strings by removing tabs, line return and removing any extra blanks.

    :param string_list: the list to normalize.
    :return: The normalized list.
    """
    line_return = re.compile(r'[\t\n]+')
    more_than_two_spaces = re.compile(r'[\s]{2,}')
    return list(map(lambda x: re.sub(
        more_than_two_spaces,
        ' ',
        re.sub(
            line_return,
            '',
            x
        )
    ).strip(), string_list))


def compare_lists(list_a, list_b, strict=False):
    """
    Compare two lists of string. If strict, compare their raw values. Otherwise normalize lists with
    normalize_list.

    :param list_a: the first list.
    :param list_b: the second list.
    :param strict: If strict, no normalization is done and the two list are compared with their raw values.
    :return: True if the lists are the same (same contents (spaces depending on strict),
    same length but not same order), False otherwise.
    """
    if 0 == len(list_a) == len(list_b):
        return True

    if not strict:
        list_a = normalize_list(list_a)
        list_b = normalize_list(list_b)

    diff = set(list_a).difference(list_b)
    if len(diff) != 0:
        print("""[normalize_and_compare_lists] {a} is not the same as {b}"""
              .format(a=diff, b=set(list_b).difference(list_a)))

    # check lists
    return len(diff) == 0 and len(list_a) == len(list_b)


def clear_input(driver, input_css_selector):
    """
    Clear an input by pressing the backspace button until the input is empty.

    :param driver: The selenium driver instance.
    :param input_css_selector: The css selector for the input to clear.
    :return: -
    """
    element = driver.find_element_by_css_selector(input_css_selector)
    for _ in range(0, len(element.get_attribute("value"))):
        element.send_keys(Keys.BACK_SPACE)


def accept_alert(driver):
    """
    Accepts any expected alert. If an alert does not show up in 5 seconds, times out and raise an exception.

    :param driver: The selenium driver instance.
    :return: -
    """
    WebDriverWait(driver, 5).until(expected_conditions.alert_is_present(), 'Timed out waiting for confirm alert.')
    alert = driver.switch_to.alert
    alert.accept()


def set_value_of_on_blur_input(driver, input_id, expected_init_value, new_value):
    """
    Sets the value of an input that gets its init value from the modification of an other input.
    
    :param driver: The selenium driver instance.
    :param input_id: The input id.
    :param expected_init_value: Expected init value (we will wait it before making the modification).
    :param new_value: The value that the input will have once it has received its init value.
    :return:
    """
    driver.find_element_by_id(input_id).click()
    WebDriverWait(driver, 5).until(
        lambda x: x.find_element_by_id(input_id).get_attribute("value") == expected_init_value)
    driver.find_element_by_id(input_id).clear()
    driver.find_element_by_id(input_id).send_keys(new_value)


def create_station(driver, tab_id, save=True, station_name="", short_name="", medium_name="", long_name="",
                   short_description="", default_language=True, url_default="", address=True, phone_number="",
                   sms_number="", sms_body="", sms_description="", email_address="", email_description="", genres=[],
                   radiovis_enabled=False, radioepg_enabled=False, radioepgpi_enabled=False, radiovis_service=None,
                   ip_allowed=None, radioepg_service=None, radiospi_service=None):
    """
    Creates a station. Goes to the station edit screen and creates a station. If one would like to save a station
    override, one has to set the 'save' parameter to False to every call but the last one of this function so the last
    call hits the save button.

    Note: By convention the tab with the station itself is the tab 0. The next from 1 to N, N being the number of
    clients, are overrides for each client. If one wish to not specify any input for a client one must leave the
    tab untouched.

    :param driver: The selenium WebDriver instance.
    :param tab_id: The id of the tab to modify.
    :param save: If True save at the end of the field edition the station. Otherwise just do the field edition.
    :param station_name: The station name.
    :param short_name: The short station name (max 8 chars).
    :param medium_name: The medium station name (max 16 chars).
    :param long_name: The long station name (max 128 chars).
    :param short_description: The short description of the station.
    :param default_language: The default language of the station. If True will copy the language from the station.
    If this parameter is not an empty string will try to find the corresponding option value in the select an select it.
    For example if one would like to select british english one would set this parameter to 'en-GB'.
    :param url_default:
    :param address: If True the address will be copied from the service provider.
    If one would like to specify a full address, one would set this parameter with a dictionary of the following shape:
    {
        'postal_name': string,
        'street': string,
        'zipcode': string,
        'city': string,
        'location_country': string, (Selenium will try find the corresponding option value in location country select
                                     and select it. For example if one would like to select Italy one would set this
                                     parameter to 'it'.)
    }
    :param phone_number: Phone number of the station.
    :param sms_number: Sms number of the station.
    :param sms_body: Sms body of the station.
    :param sms_description: Email description of the station.
    :param email_address: Email address of the station (no verifications done yet OPENRADIO-38).
    :param email_description: Email description.
    :param genres: List of string that contains option value to be used as css selector to select a genre of the station.
    For example, if one would like to have Rock and Metal genre on the station, one would set this parameter to
    ['3.6.4.14', '3.6.4.14.2']. This list of values is in the select of any genre and also in the map of genres in the
    <ROOT_FOLDER>/RadioDns-PlugIt/station/utils.py file.
    Note: This parameter only allow to add genre. If you were to modify existing ones, you would have to do it outside
    this function and leave this parameter to only the genres you want to add.
    :param radiovis_enabled: If the radiovis should be enabled. Note that this parameter is relevant only for tab 0.
    :param radioepg_enabled: If the radioepg should be enabled. Note that this parameter is relevant only for tab 0.
    :param radioepgpi_enabled: If the radioepgi should be enabled. Note that this parameter is relevant only for tab 0.
    :param radiovis_service:If the radiospi should be enabled. Note that this parameter is relevant only for tab 0.
    :param ip_allowed: Parameter for the radiovis service. Specify which ips are allowed to be connected to the vis service.
    :param radioepg_service: Host for the radioepg service. Can be a hostname or a static ip.
    :param radiospi_service: Host for the radiospi service. Can be a hostname or a static ip.
    :return:
    """
    driver.find_element_by_id("station-name_" + str(tab_id)).send_keys(station_name)
    if short_name != "":
        set_value_of_on_blur_input(driver, "short_name_" + str(tab_id), station_name[:8], short_name)
    if medium_name != "":
        set_value_of_on_blur_input(driver, "medium_name_" + str(tab_id), short_name, medium_name)
    if long_name != "":
        set_value_of_on_blur_input(driver, "long_name_" + str(tab_id), medium_name, long_name)
    if short_description != "":
        set_value_of_on_blur_input(driver, "short_description_" + str(tab_id), long_name, short_description)

    if default_language is True:
        driver.find_element_by_id("copyLanguageButton_" + str(tab_id)).click()
    elif len(default_language) > 0:
        driver.find_element_by_id("default_language_" + str(tab_id)) \
            .find_element_by_css_selector("""option[value='{value}']""".format(value=default_language)).click()

    driver.find_element_by_name("url_default_" + str(tab_id)).send_keys(url_default)

    if address is True:
        driver.find_element_by_id("copyAddressButton_" + str(tab_id)).click()
    elif address:
        driver.find_element_by_id("postal_name_" + str(tab_id)).send_keys(address["postal_name"])
        driver.find_element_by_id("street_" + str(tab_id)).send_keys(address["street"])
        driver.find_element_by_id("zipcode_" + str(tab_id)).send_keys(address["zipcode"])
        driver.find_element_by_id("city_" + str(tab_id)).send_keys(address["city"])
        driver.find_element_by_id("location_country_" + str(tab_id)) \
            .find_element_by_css_selector("""option[value='{value}']""".format(value=address["location_country"])).click()

    driver.find_element_by_id("phone_number_" + str(tab_id)).send_keys(phone_number)
    driver.find_element_by_id("sms_number_" + str(tab_id)).send_keys(sms_number)
    driver.find_element_by_id("sms_body_" + str(tab_id)).send_keys(sms_body)
    driver.find_element_by_id("sms_description_" + str(tab_id)).send_keys(sms_description)
    driver.find_element_by_id("email_address_" + str(tab_id)).send_keys(email_address)
    driver.find_element_by_id("email_description_" + str(tab_id)).send_keys(email_description)

    for i, genre in enumerate(genres):
        driver.find_element_by_id("add_gender_button_" + str(tab_id)).click()
        index = i if tab_id == 0 else i + 1
        driver.find_element_by_id("""genre-select-{i}_{id}""".format(id=str(tab_id), i=index))\
            .find_element_by_css_selector("""option[value='{value}']""".format(value=genre)).click()

    if tab_id == 0:
        if radiovis_enabled:
            driver.find_element_by_id("radiovis_enabled_" + str(tab_id)).click()
            clear_input(driver, "#radiovis_service_" + str(tab_id))
            driver.find_element_by_id("radiovis_service_" + str(tab_id)).send_keys(radiovis_service)
            driver.find_element_by_id("ip_allowed_0" + str(tab_id)).send_keys(ip_allowed)

        if radioepg_enabled:
            driver.find_element_by_id("radioepg_enabled_" + str(tab_id)).click()
            clear_input(driver, "#radioepg_service_" + str(tab_id))
            driver.find_element_by_id("radioepg_service_" + str(tab_id)).send_keys(radioepg_service)
            clear_input(driver, "#radiospi_service_" + str(tab_id))
            driver.find_element_by_id("radiospi_service_" + str(tab_id)).send_keys(radiospi_service)

        if radioepgpi_enabled:
            driver.find_element_by_id("radioepgpi_enabled_" + str(tab_id)).click()

    if save:
        driver.find_element_by_css_selector("button[type=submit][value=Save]").click()
