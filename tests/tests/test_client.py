from functools import reduce

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import text

from tests.conftest import TEST_PROXY_URL
from tests.utilities.utilities import compare_lists, sql_alchemy_result_to_list, clear_input, accept_alert

CLIENTS_HTML_TR = [
    "\n".join(["BBC", "contact@bbc.com", "Copy", "TESTIDENTIFIERS1", "Edit Delete"]),
    "\n".join(["CNN", "contact@cnn.com", "Copy", "TESTIDENTIFIERS2", "Edit Delete"]),
]

CLIENTS_DB_TR = [
    " ".join(["BBC", "contact@bbc.com", "TESTIDENTIFIERS1"]),
    " ".join(["CNN", "contact@cnn.com", "TESTIDENTIFIERS2"]),
]

CLIENTS_MYSQL_QUERY = "SELECT name, email, identifier FROM clients"


@pytest.mark.run(order=3)
def test_client_creation(stack_setup, browser_setup):
    """Default behavior test with no faulty input."""
    db = stack_setup
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_creation_toggle_button"))
    driver.find_element_by_id("client_creation_toggle_button").click()

    # create first client
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_name_new"))
    driver.find_element_by_id("client_name_new").send_keys("BBC")
    driver.find_element_by_id("client_email_new").send_keys("contact@bbc.com")
    driver.find_element_by_id("new_client_identifier_suggestion").click()
    assert len(driver.find_element_by_id("client_identifier_new").get_attribute('value')) == 128
    driver.find_element_by_id("client_identifier_new").clear()
    driver.find_element_by_id("client_identifier_new").send_keys("TESTIDENTIFIERS1")
    driver.find_element_by_id("update_save_btn_new").click()
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_row_1"))

    # create a second client
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_name_new"))
    driver.find_element_by_id("client_name_new").send_keys("CNN")
    driver.find_element_by_id("client_email_new").send_keys("contact@cnn.com")
    driver.find_element_by_id("client_identifier_new").send_keys("TESTIDENTIFIERS2")
    driver.find_element_by_id("update_save_btn_new").click()
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_row_2"))

    # Check entered data
    clients_tr = list(map(lambda x: x.text, driver
                          .find_element_by_id("clients_display")
                          .find_elements_by_css_selector("tr")))
    assert compare_lists(clients_tr, CLIENTS_HTML_TR)

    # Check DB
    result = db.engine.execute(text(CLIENTS_MYSQL_QUERY))
    assert result.rowcount == 2
    client_mysql_tr = []
    for row in sql_alchemy_result_to_list(result):
        client_mysql_tr.append(reduce(lambda x, y: str(x) + " " + str(y), row))
    assert compare_lists(client_mysql_tr, CLIENTS_DB_TR, True)


def test_create_client_empty_inputs(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()


def test_create_client_no_username(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_creation_toggle_button"))
    driver.find_element_by_id("client_creation_toggle_button").click()

    driver.find_element_by_id("client_email_new").send_keys("contact@bbc.com")
    driver.find_element_by_id("new_client_identifier_suggestion").click()
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()


def test_create_client_invalid_email(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_creation_toggle_button"))
    driver.find_element_by_id("client_creation_toggle_button").click()

    driver.find_element_by_id("client_name_new").send_keys("BBC")
    driver.find_element_by_id("new_client_identifier_suggestion").click()
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()

    driver.find_element_by_id("client_email_new").send_keys("contactbbc.com")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()

    driver.find_element_by_id("client_email_new").send_keys("contact@bbccom")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()


def test_create_client_invalid_identifier(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_creation_toggle_button"))

    driver.find_element_by_id("client_creation_toggle_button").click()

    driver.find_element_by_id("client_name_new").send_keys("BBC")
    driver.find_element_by_id("client_email_new").send_keys("contact@bbc.com")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()

    driver.find_element_by_id("client_identifier_new").send_keys("123456789")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()

    driver.find_element_by_id("client_identifier_new").send_keys("dfégbdfspgdfsgsufpadfhp232!!!")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()

    driver.find_element_by_id("client_identifier_new").send_keys(
        "k2unCjphD7W6SDf67zddr4Y3EfGghxCHY4Fdtbm2ajNiUZKjMTUPjxayaxzXwTNYtwEHgwQiM7w846NJRenTzHCwGVwYWTVzNXHZD2X7k3m"
        "NDKUnMuGMxND27YpidRhmBiFntY44qmiivDKa3anRvwKgqNGJ9Gx3DNJr4i9QWPRSzXDgam9jqen2pNMnpj7nvc7Wm75J")
    assert not driver.find_element_by_id("update_save_btn_new").is_enabled()


def test_update_client_no_changes(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("toggle_edit_btn_1"))

    # Check if rendered correctly
    driver.find_element_by_id("toggle_edit_btn_1").click()
    driver.find_element_by_id("client_name_1")
    driver.find_element_by_id("client_email_1")
    driver.find_element_by_id("client_identifier_1")
    driver.find_element_by_id("cancel_update_save_btn_1")

    # Check functionality
    driver.find_element_by_id("update_save_btn_1").click()
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))


def test_update_client_name(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("toggle_edit_btn_1"))
    driver.find_element_by_id("toggle_edit_btn_1").click()

    # Test with empty name
    clear_input(driver, "#client_name_1")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    # Test with pre-existing name
    driver.find_element_by_id("client_name_1").send_keys("CNN")
    assert driver.find_element_by_id("update_save_btn_1").is_enabled()
    driver.find_element_by_id("update_save_btn_1").click()
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("ajax_error_display").find_element_by_tag_name("li"))
    assert driver.find_element_by_id("ajax_error_display").find_element_by_tag_name("li").text \
           == "A client with this name already exists."

    # Test with new name
    driver.find_element_by_id("client_name_1").send_keys("BBC2")
    driver.find_element_by_id("update_save_btn_1").click()
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))


def test_update_client_email(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("toggle_edit_btn_1"))
    driver.find_element_by_id("toggle_edit_btn_1").click()

    # Test with empty email
    clear_input(driver, "#client_email_1")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    # Test with malformed email
    clear_input(driver, "#client_email_1")
    driver.find_element_by_id("client_email_1").send_keys("contactbbc.com")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    clear_input(driver, "#client_email_1")
    driver.find_element_by_id("client_email_1").send_keys("contact@bbccom")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    # Test with correct email
    clear_input(driver, "#client_email_1")
    driver.find_element_by_id("client_email_1").send_keys("contact@bbc.com")
    assert driver.find_element_by_id("update_save_btn_1").is_enabled()

    # Test update
    driver.find_element_by_id("update_save_btn_1").click()
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))


def test_update_client_identifier(stack_setup, browser_setup):
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("toggle_edit_btn_1"))
    driver.find_element_by_id("toggle_edit_btn_1").click()

    # Test with empty identifier
    clear_input(driver, "#client_identifier_1")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    # Test with malformed identifier
    driver.find_element_by_id("client_identifier_1").send_keys("123456789")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    driver.find_element_by_id("client_identifier_1").send_keys("dfégbdfspgdfsgsufpadfhp232!!!")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    driver.find_element_by_id("client_identifier_1").send_keys(
        "k2unCjphD7W6SDf67zddr4Y3EfGghxCHY4Fdtbm2ajNiUZKjMTUPjxayaxzXwTNYtwEHgwQiM7w846NJRenTzHCwGVwYWTVzNXHZD2X7k3m"
        "NDKUnMuGMxND27YpidRhmBiFntY44qmiivDKa3anRvwKgqNGJ9Gx3DNJr4i9QWPRSzXDgam9jqen2pNMnpj7nvc7Wm75J")
    assert not driver.find_element_by_id("update_save_btn_1").is_enabled()

    # Test with pre-existing identifier
    clear_input(driver, "#client_identifier_1")
    driver.find_element_by_id("client_identifier_1").send_keys("TESTIDENTIFIERS2")
    assert driver.find_element_by_id("update_save_btn_1").is_enabled()
    driver.find_element_by_id("update_save_btn_1").click()
    accept_alert(driver)

    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("ajax_error_display")
                                   .find_element_by_tag_name(
        "li").text == "A client with this identifier already exists.")

    # Test update
    driver.find_element_by_id("client_identifier_1").send_keys("TESTIDENTIFIERS2345")
    driver.find_element_by_id("update_save_btn_1").click()
    accept_alert(driver)
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))


@pytest.mark.last
def test_delete_client(stack_setup, browser_setup):
    db = stack_setup
    driver = browser_setup

    driver.get(TEST_PROXY_URL + "clients/")
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("toggle_edit_btn_1"))
    driver.find_element_by_id("cancel_edit_btn_1").click()
    accept_alert(driver)
    WebDriverWait(driver, 5).until(lambda x: x.find_element_by_id("client_operation_success"))
    WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, "client_row_1")))

    # Check data
    clients_tr = sorted(list(map(lambda x: x.text, driver
                          .find_element_by_id("clients_display")
                          .find_elements_by_css_selector("tr"))))
    assert len(clients_tr) == 2
    assert clients_tr[0] == ""
    assert clients_tr[1] == CLIENTS_HTML_TR[1]

    # Check DB
    result = db.engine.execute(text(CLIENTS_MYSQL_QUERY))
    assert result.rowcount == 1
    client_mysql_tr = []
    for row in sql_alchemy_result_to_list(result):
        client_mysql_tr.append(reduce(lambda x, y: str(x) + " " + str(y), row))
    assert client_mysql_tr[0] == CLIENTS_DB_TR[1]
