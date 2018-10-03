import os

from tests.conftest import TEST_PROXY_URL


def test_image_edit_no_inputs(stack_setup, browser_setup):
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/images/edit/-")
    assert driver.find_element_by_id("img_file_input").get_attribute("value") == ""
    assert driver.find_element_by_id("name").get_attribute("value") == ""
    a = driver.find_element_by_id("img_save").get_attribute("disabled")
    assert driver.find_element_by_id("img_save").get_attribute("disabled") == "true"


def test_image_edit_only_name_entered(stack_setup, browser_setup):
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/images/edit/-")
    driver.find_element_by_id("name").send_keys("")
    assert driver.find_element_by_id("img_save").get_attribute("disabled") == "true"


def test_image_edit_only_file_entered(stack_setup, browser_setup):
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/images/edit/-")
    driver.find_element_by_id("img_file_input").send_keys(os.getcwd() + "/ressources/classical_music.jpg")
    assert driver.find_element_by_id("img_save").get_attribute("disabled") == "true"


def test_image_edit_every_required_fields_filled(stack_setup, browser_setup):
    driver = browser_setup
    driver.get(TEST_PROXY_URL + "serviceprovider/images/edit/-")
    driver.find_element_by_id("name").send_keys("TEST")
    driver.find_element_by_id("img_file_input").send_keys(os.getcwd() + "/ressources/classical_music.jpg")
    assert driver.find_element_by_id("img_save").get_attribute("disabled") is None
