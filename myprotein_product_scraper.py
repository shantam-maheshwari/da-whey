"""
Creates a Product object from a product url.
"""

import logging
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from product import Product


class MyproteinProductScraper:
    def __init__(self, url: str, headless: bool = False):
        self._url = url
        self._driver = self._get_driver(headless)
        self._wait = WebDriverWait(self._driver, 10)

        self._driver.get(url)
        self._reject_all_cookies()
        self._close_email_popup()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._driver.close()
        self._driver.quit()

    def _get_driver(self, headless: bool) -> WebDriver:
        brave_path = "/usr/bin/brave-browser"
        driver_path = "/usr/local/bin/chromedriver"

        options = webdriver.ChromeOptions()
        options.headless = headless
        options.binary_location = brave_path
        service = Service(driver_path)
        driver = webdriver.Chrome(options, service)
        return driver

    def _reject_all_cookies(self):
        select_prefs_btn_locator = (By.ID, "onetrust-pc-btn-handler")
        self._wait.until(EC.element_to_be_clickable(select_prefs_btn_locator))
        select_prefs_btn = self._driver.find_element(*select_prefs_btn_locator)
        select_prefs_btn.click()

        reject_all_btn_locator = (By.CLASS_NAME, "ot-pc-refuse-all-handler")
        self._wait.until(EC.element_to_be_clickable(reject_all_btn_locator))
        reject_all_btn = self._driver.find_element(*reject_all_btn_locator)
        reject_all_btn.click()

    def _close_email_popup(self):
        close_btn_locator = (By.CLASS_NAME, "emailReengagement_close_button")
        self._wait.until(EC.element_to_be_clickable(close_btn_locator))
        close_btn = self._driver.find_element(*close_btn_locator)
        close_btn.click()

    def scrape(self) -> Product:
        product_name = self._get_product_name()
        logging.info(f"Scraping product: {product_name}")
        product_flavours = self._get_product_flavours()
        product = Product(product_name, self._url, product_flavours)
        return product

    def _get_product_name(self) -> str:
        product_name_locator = (By.CLASS_NAME, "productName_title")
        product_name = self._driver.find_element(*product_name_locator).text
        return product_name

    def _get_product_flavours(self) -> list:
        flavour_option_locator = (
            By.CSS_SELECTOR,
            "select#athena-product-variation-dropdown-5 > option",
        )
        flavour_options = self._driver.find_elements(*flavour_option_locator)
        number_of_flavours = len(flavour_options)
        logging.info(f"\tNumber of flavours: {number_of_flavours}")

        flavour_names = [option.text.strip() for option in flavour_options]
        flavour_price_infos = [
            self._get_nth_flavour_price_info(i)
            for i in range(number_of_flavours)
        ]
        return list(zip(flavour_names, flavour_price_infos))

    def _get_nth_flavour_price_info(self, n: int) -> list:
        logging.info(f"\tScraping prices for flavour: {n+1}")
        self._select_nth_flavour(n)

        amount_btn_locator = (
            By.CLASS_NAME,
            "athenaProductVariations_box.default.athenaProductVariationsOption",
        )
        amount_btns = self._driver.find_elements(*amount_btn_locator)
        number_of_amounts = len(amount_btns)

        amounts = [btn.text.strip() for btn in amount_btns]
        prices = [
            self._get_nth_amount_price(i) for i in range(number_of_amounts)
        ]
        return list(zip(amounts, prices))

    def _select_nth_flavour(self, n: int):
        flavour_select_locator = (By.ID, "athena-product-variation-dropdown-5")
        self._wait.until(EC.element_to_be_clickable(flavour_select_locator))
        flavour_select = self._driver.find_element(*flavour_select_locator)
        flavour_selector = Select(flavour_select)
        flavour_selector.select_by_index(n)
        time.sleep(1)

    def _get_nth_amount_price(self, n: int) -> float:
        self._select_nth_amount(n)

        product_price_locator = (By.CLASS_NAME, "productPrice_price")

        floatify = lambda str: float(
            re.compile(r"([0-9]+\.[0-9]+)").search(str).group()
        )

        product_price = self._driver.find_element(*product_price_locator)
        product_price = floatify(product_price.text)
        return product_price

    def _select_nth_amount(self, n: int):
        amount_btn_locator = (
            By.CSS_SELECTOR,
            f".athenaProductVariations_list li:nth-of-type({n+1}) button",
        )
        self._wait.until(EC.element_to_be_clickable(amount_btn_locator))
        amount_btn = self._driver.find_element(*amount_btn_locator)
        amount_btn.click()
        time.sleep(1)
