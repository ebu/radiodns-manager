import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

from tests.conftest import TEST_PROXY_URL


def check_override_creation_for_input(
        driver,
        dom_id,
        group,
        set_value=lambda elem, value: elem.send_keys(value),
        read_value=lambda elem: elem.get_attribute("value") if elem.get_attribute("value") else elem.get_attribute(
            "placeholder"),
        clear_value=lambda elem: elem.clear(),
        original_value="origin",
        override_value="override",
        new_value="newVal",
        after_loading=lambda *args, **kwargs: None):
    driver.get(TEST_PROXY_URL + "stations/edit/-")
    after_loading()

    # Fill inputs
    set_value(driver.find_element_by_id(dom_id + "0"), original_value)

    # Fill overrides on tab 1
    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)
    set_value(driver.find_element_by_id(dom_id + "1"), override_value)
    assert driver.find_element_by_id("dot_grp_1_" + group).value_of_css_property("opacity") == "1"

    # Assert that override had no effect on original input

    driver.find_element_by_id("nav_tab_0").send_keys(Keys.RETURN)
    assert read_value(driver.find_element_by_id(dom_id + "0")) == original_value

    # Set new values override
    clear_value(driver.find_element_by_id(dom_id + "0"))
    set_value(driver.find_element_by_id(dom_id + "0"), new_value)

    # Assert that override can be reset and take the corresponding value of the default tab.
    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)
    assert read_value(driver.find_element_by_id(dom_id + "1")) == override_value
    driver.find_element_by_id("reset-override-" + group + "-btn_1").click()
    assert read_value(driver.find_element_by_id(dom_id + "1")) == new_value


def test_station_ui_overrides(stack_setup, browser_setup):
    driver = browser_setup

    select_set_value = lambda elem, value: elem.find_element_by_css_selector("option[value='" + value + "']").click()
    select_read_value = lambda elem: Select(elem).first_selected_option.get_attribute("value")
    select_clear_value = lambda e: e

    check_override_creation_for_input(driver, "station-name_", "name")
    check_override_creation_for_input(driver, "short_description_", "name")

    check_override_creation_for_input(
        driver,
        "default_language_",
        "language",
        select_set_value,
        select_read_value,
        select_clear_value,
        'af',
        'ak',
        'an',
    )

    check_override_creation_for_input(driver, "default_url_", "links")

    check_override_creation_for_input(driver, "postal_name_", "address")
    check_override_creation_for_input(driver, "street_", "address")
    check_override_creation_for_input(driver, "zipcode_", "address")
    check_override_creation_for_input(driver, "city_", "address")

    check_override_creation_for_input(
        driver,
        "location_country_",
        "address",
        select_set_value,
        select_read_value,
        select_clear_value,
        "al",
        "dz",
        "ao",
        lambda *args, **kwargs: time.sleep(0.5)
    )

    check_override_creation_for_input(driver, "phone_number_", "contact")
    check_override_creation_for_input(driver, "sms_number_", "contact")
    check_override_creation_for_input(driver, "sms_body_", "contact")
    check_override_creation_for_input(driver, "sms_description_", "contact")
    check_override_creation_for_input(driver, "email_address_", "contact")
    check_override_creation_for_input(driver, "email_description_", "contact")


def test_station_ui_overrides_genres(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "stations/edit/-")

    # Add genres on default tab
    driver.find_element_by_id("add_gender_button_0").click()
    driver.find_element_by_id("genre_row_template_0-0").find_element_by_css_selector(
        "option[value='3.6.4.14']").click()  # Rock
    driver.find_element_by_id("add_gender_button_0").click()
    driver.find_element_by_id("genre_row_template_0-1").find_element_by_css_selector(
        "option[value='3.6.10']").click()  # Hit-Chart
    driver.find_element_by_id("add_gender_button_0").click()
    driver.find_element_by_id("genre_row_template_0-2").find_element_by_css_selector(
        "option[value='3.6.4.14.2']").click()  # Metal

    # Make overrides on tab 1
    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)

    # Change first genre
    driver.find_element_by_id("genre_row_template_1-0").find_element_by_css_selector(
        "option[value='3.3.5']").click()  # Travel

    # Remove other genres
    driver.find_element_by_id("genre_row_template_1-1").find_element_by_css_selector(
        ".btn.btn-xs.btn-danger").click()
    driver.find_element_by_id("genre_row_template_1-2").find_element_by_css_selector(
        ".btn.btn-xs.btn-danger").click()

    # Add new genres
    driver.find_element_by_id("add_gender_button_1").click()
    driver.find_element_by_id("genre_row_template_1-4").find_element_by_css_selector(
        "option[value='3.6.4.14.2']").click()  # Metal
    driver.find_element_by_id("add_gender_button_1").click()
    driver.find_element_by_id("genre_row_template_1-5").find_element_by_css_selector(
        "option[value='3.1.1.12']").click()  # Traffic
    assert driver.find_element_by_id("dot_grp_1_genres").value_of_css_property("opacity") == "1"

    # Come back on default tab
    driver.find_element_by_id("nav_tab_0").send_keys(Keys.RETURN)

    # Remove metal genre from default
    driver.find_element_by_id("genre_row_template_0-2").find_element_by_css_selector(
        ".btn.btn-xs.btn-danger").click()

    # Change genre from Rock to Service information
    driver.find_element_by_id("genre_row_template_0-0").find_element_by_css_selector(
        "option[value='3.1.1.14']").click()  # Service information

    # return on tab 1
    driver.find_element_by_id("nav_tab_1").send_keys(Keys.RETURN)
    assert driver.find_element_by_id("dot_grp_1_genres").value_of_css_property("opacity") == "1"
    assert Select(driver.find_element_by_id("genre_row_template_1-0").find_element_by_tag_name("select")) \
               .first_selected_option.text == "Travel (PTy 22 - Travel)"
    assert Select(driver.find_element_by_id("genre_row_template_1-4").find_element_by_tag_name("select")) \
               .first_selected_option.text == "Metal"
    assert Select(driver.find_element_by_id("genre_row_template_1-5").find_element_by_tag_name("select")) \
               .first_selected_option.text == "Traffic"

    # Reset override
    driver.find_element_by_id("reset-override-genres-btn_1").click()

    assert Select(driver.find_element_by_id("genre_row_template_1-0").find_element_by_tag_name("select")) \
               .first_selected_option.text == "Service information"
    assert Select(driver.find_element_by_id("genre_row_template_1-1").find_element_by_tag_name("select")) \
               .first_selected_option.text == "Hit-Chart/Song Requests"
