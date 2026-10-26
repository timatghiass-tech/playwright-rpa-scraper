import asyncio
import json
from playwright.async_api import async_playwright

class BookScraper:
    """
    Asynchronous Web Scraper built with Playwright for automated data extraction.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def scrape_category(self, category_name: str, output_file: str):
        """
        Navigates to a specific product category, extracts details, and saves results to JSON.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            print(f"[*] Accessing target URL: {self.base_url}")
            await page.goto(self.base_url)

            print(f"[*] Selecting category: '{category_name}'...")
            category_link = page.get_by_role("link", name=category_name)
            await category_link.click()

            # Wait for products to render
            await page.wait_for_selector("article.product_pod")

            print(f"[*] Extracting product information...")
            products = await page.locator("article.product_pod").all()
            
            scraped_data = []

            for product in products:
                title = await product.locator("h3 a").get_attribute("title")
                price = await product.locator("p.price_color").inner_text()
                availability = await product.locator("p.instock.availability").inner_text()

                scraped_data.append({
                    "category": category_name,
                    "title": title,
                    "price": price,
                    "availability": availability.strip()
                })

            # Save extracted data to JSON file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4)

            print(f"[+] Success! {len(scraped_data)} items exported to '{output_file}'.")
            await browser.close()


async def main():
    BASE_URL = "https://books.toscrape.com/"
    scraper = BookScraper(base_url=BASE_URL)
    
    # Run the automation pipeline
    await scraper.scrape_category(category_name="Sequential Art", output_file="sequential_art_books.json")


if __name__ == "__main__":
    asyncio.run(main())
