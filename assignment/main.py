from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent= Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

URL = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

driver.get(URL)

products = driver.find_elements(By.XPATH, "//*[@id=\"search\"]/div[1]/div[1]/div/span[1]/div[1]/div/div/div/div/div/div/div[2]/div/div/div[1]/h2/a")

class BagProduct:
    def __init__(self, url, name, price, rating, reviewerCount):
        self.url = url
        self.name = name
        self.price = price
        self.rating = rating
        self.reviewerCount = reviewerCount
        self.description = ""
        self.asin = ""
        self.manufacturer = ""
        
    def to_dict(self):
        return {
            "url": self.url,
            "name": self.name,
            "price": self.price,
            "rating": self.rating,
            "reviewerCount": self.reviewerCount,
            "description": self.description,
            "asin": self.asin,
            "manufacturer": self.manufacturer
        }

bag_products = []

def scrape_product(bag_product: BagProduct):
    try:
        driver.get(bag_product.url)
        bulletDetails = driver.find_elements(By.XPATH, "//div[@id='feature-bullets']/ul/li")
        details = ""
        for bulletDetail in bulletDetails:
            try:
                details = details + bulletDetail.find_element(By.XPATH, "span").text + "\n"
            except:
                pass
        bag_product.description = details
        
        try:
            product_detail_bullets = driver.find_element(By.XPATH, "//div[@data-feature-name='detailBullets']")
            bullet_keys = product_detail_bullets.find_elements(By.XPATH, "div[@id='detailBullets_feature_div']/ul/li/span")
            for bullet_key in bullet_keys:
                name = bullet_key.find_element(By.XPATH, "span[1]").text
                value = bullet_key.find_element(By.XPATH, "span[2]").text
                if "Manufacturer" in name:
                    bag_product.manufacturer = value
                elif "ASIN" in name:
                    bag_product.asin = value
        except:
            try:
                rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'prodDetTable')]/tbody/tr")
                for row in rows:
                    name = row.find_element(By.XPATH, "th").text
                    value = row.find_element(By.XPATH, "td").text
                    if "Manufacturer" in name:
                        bag_product.manufacturer = value
                    elif "ASIN" in name:
                        bag_product.asin = value
            except:
                pass
        
        if len(bag_product.manufacturer) == 0:
            try:
                brand_name = driver.find_element(By.XPATH, "//div[contains(@class, 'brand-snapshot-flex-row')]/p/span").text
                bag_product.manufacturer = brand_name
            except:
                pass
    except:
        pass


def scrape_current_page():
    products = driver.find_elements(By.XPATH, "//*[contains(@cel_widget_id, 'MAIN-SEARCH_RESULTS')]/div/div/div/div[2]")
    for product in products:
        try:
            url = product.find_element(By.XPATH, "div/div/div/h2/a")
            urlStr = url.get_attribute("href")
            
            title = product.find_element(By.XPATH, "div/div/div/h2/a/span")
            titleStr = title.text
            
            price = product.find_element(By.XPATH, "div/div/div[3]/div/div/div[1]/div[contains(@class, 'a-color-base')]/a/span[1]/span[2]/span[2]")
            priceStr = price.get_attribute("innerHTML")
            
            rating = product.find_element(By.XPATH, "div/div/div[2]/div/span[1]")
            ratingStr = rating.get_attribute("aria-label")[0:3]
            
            reviewerCount = product.find_element(By.XPATH, "div/div/div[2]/div/span[2]")
            reviewerCountStr = reviewerCount.get_attribute("aria-label")
        
        
            bag_products.append(BagProduct(urlStr, titleStr, priceStr, ratingStr, reviewerCountStr))
        except Exception as e:
            pass


def go_to_next_page(page_num):
    try:
        driver.get(URL + "&page=" + str(page_num))
        return True
    except:
        return False

print("Crawling all pages to find list of products.")
scrape_current_page()
for i in range(2, 21):
    go_to_next_page(i)
    scrape_current_page()

print("Found total " + str(len(bag_products)) + " products.")
print ("Starting scrape for each product.")

i = 0
for bp in bag_products:
    i = i + 1
    if (i % 10 == 0):
        print ("Scraped " + str(i) + " products till now.")
    scrape_product(bp)

bag_df = pd.DataFrame.from_records([bp.to_dict() for bp in bag_products])
bag_df.to_csv("products.csv")
    

