import logging
from pprint import pprint

from myprotein_product_scraper import MyproteinProductScraper

product_url = r"https://www.myprotein.com/sports-nutrition/impact-whey-protein"

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="output.log",
    )

    with MyproteinProductScraper(
        product_url,
        False,
    ) as scraper:
        product = scraper.scrape()
        pprint(product)
