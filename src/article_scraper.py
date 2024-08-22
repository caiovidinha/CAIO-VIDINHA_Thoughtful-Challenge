import logging
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.keys import Keys
from src.article import Article 
from src.image_downloader import ImageDownloader 
from src.excel_saver import ExcelSaver 
from src.date_parser import DateParser 

class ArticleScraper:
    def __init__(self, url, search_text, category="Date", number_of_months=1):
        self.url = url
        self.search_text = search_text
        self.category = category
        self.number_of_months = number_of_months
        self.browser = Selenium()
        self.downloader = ImageDownloader()
        self.excel_saver = ExcelSaver()
        self.articles = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def open_browser(self):
        """Opens the browser and navigates to the URL."""
        self.logger.info("Opening browser and navigating to URL: %s", self.url)
        self.browser.open_available_browser(self.url, maximized=True)

    def search_articles(self):
        """Performs the search based on the given search text."""
        self.logger.info("Performing search for text: %s", self.search_text)
        self.browser.click_element("xpath://button[@type='button']")
        self.browser.input_text("xpath://input[@placeholder='Search']", self.search_text)
        self.browser.press_key("xpath://input[@placeholder='Search']", Keys.ENTER)
        self.browser.click_element_when_visible("id:search-sort-option")
        try:

            self.browser.click_element_when_visible(f"xpath://option[@value='{self.category.lower()}']")
        except Exception as e:
            logging.warning(f"Could not find category '{self.category.lower()}'. Defaulting to 'relevance'. Error: {e}")
            self.browser.click_element_when_visible("xpath://option[@value='relevance']")

    def process_articles(self):
        """Processes the articles found during the search."""
        self.logger.info("Processing articles...")
        article_index = 1
        while True:
            try:
                title_xpath = f"(//h3[@class='gc__title']/a)[{article_index}]"
                description_xpath = f"(//article//p)[{article_index}]"
                img_xpath = f"(//article//img)[{article_index}]"

                try:
                    self.browser.wait_until_page_contains_element(title_xpath, timeout=5)
                except Exception as e:
                    self.logger.warning("Title element not found: %s", e)
                    if not self.click_show_more_button():
                        self.logger.info("No more articles to load.")
                        break
                    continue

                title = self.browser.get_text(title_xpath)
                date_and_description = self.browser.get_text(description_xpath)
                unparsed_date, description = Article.extract_date_and_clean_description(date_and_description)
                article_date = DateParser.parse_aljazeera_date(unparsed_date)

                if not article_date or not DateParser.is_within_date_range(article_date, self.number_of_months):
                    article_index += 1
                    continue

                img_url = self.browser.get_element_attribute(f"xpath:{img_xpath}", "src") if self.browser.is_element_visible(img_xpath) else None

                article = Article(title, description, unparsed_date, img_url)
                
                article.download_image(self.downloader)

                search_phrase_occurrences = article.count_search_phrases(self.search_text)
                contains_money = article.contains_money()

                article_data = article.to_list(search_phrase_occurrences, contains_money)
                self.articles.append(article_data)
                self.logger.info("Processed article %d: %s", article_index, title)

            except Exception as e:
                self.logger.error("Error processing article %d: %s", article_index, e)

            article_index += 1

    def click_show_more_button(self):
        """Clicks the 'Show More' button if it is present."""
        try:
            self.browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
            show_more_button_xpath = "//button[@data-testid='show-more-button']"
            if self.browser.is_element_visible(show_more_button_xpath):
                self.browser.click_button(show_more_button_xpath)
                self.browser.wait_until_element_is_not_visible(show_more_button_xpath, timeout=10)
                self.logger.info("Clicked 'Show More' and loaded more results.")
                return True
        except Exception as e:
            self.logger.error("Error clicking 'Show More': %s", e)
        return False

    def close_browser(self):
        """Closes the browser."""
        self.logger.info("Closing all browsers.")
        self.browser.close_all_browsers()

    def scrape(self):
        """Main method to run the entire scraping process."""
        self.logger.info("Starting scraping process.")
        self.open_browser()
        self.search_articles()
        self.process_articles()
        self.close_browser()

        if self.articles:
            headers = ["Title", "Date", "Description", "Image Filename", "Search Phrase Occurrences", "Contains Money"]
            self.excel_saver.save(self.articles, headers)
            self.logger.info("Saved articles to Excel.")
        else:
            self.logger.info("No articles were saved.")
