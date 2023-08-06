from pprint import pprint

from myprotein_product_scraper import MyproteinProductScraper

product_url = r"https://www.myprotein.com/sports-nutrition/impact-whey-protein"

if __name__ == "__main__":
    with MyproteinProductScraper(
        product_url,
        False,
    ) as scraper:
        product = scraper.scrape()
        pprint(product)
