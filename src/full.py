"""Module to scrape and analyze articles from Al Jazeera."""

import uuid
import re
from datetime import datetime, timedelta
import requests
from dateutil import parser
from RPA.Browser.Selenium import Selenium
from RPA.FileSystem import FileSystem
from RPA.Excel.Files import Files
from selenium.webdriver.common.keys import Keys


def parse_aljazeera_date(date_str):
    """Parses relative or absolute date strings into a standardized format."""
    relative_pattern = re.compile(r'(\d+)\s+(minute|minutes|hour|hours|day|days)\s+ago')
    match = relative_pattern.match(date_str.lower())

    if match:
        value, unit = int(match.group(1)), match.group(2)
        if 'minute' in unit:
            delta = timedelta(minutes=value)
        elif 'hour' in unit:
            delta = timedelta(hours=value)
        elif 'day' in unit:
            delta = timedelta(days=value)
        else:
            return None
        parsed_date = datetime.now() - delta
    else:
        try:
            parsed_date = parser.parse(date_str)
        except (ValueError, OverflowError):
            return None

    return parsed_date.strftime('%d-%m-%Y')


def extract_date_and_clean_description(desc):
    """Extracts the date from the description and cleans up the description text."""
    try:
        if not desc or not isinstance(desc, str):
            raise ValueError("Descrição inválida ou vazia.")

        relative_pattern = r'\d+\s+(minute|minutes?|hour|hours?|day|days?)\s+ago'
        absolute_pattern = r'[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}'
        full_pattern = f'({relative_pattern})|({absolute_pattern})'

        date_match = re.search(full_pattern, desc)
        if not date_match:
            raise ValueError("Nenhuma data encontrada na descrição.")

        date_str = date_match.group(0)
        cleaned_description = re.sub(full_pattern, '', desc).strip()

        # Remove any leading special characters before the first letter
        cleaned_description = re.sub(r'^[^a-zA-Z]+', '', cleaned_description)

        if not cleaned_description:
            raise ValueError("Descrição ficou vazia após a remoção da data e dos '...'.")

        return date_str, cleaned_description

    except ValueError as ve:
        print(f"Erro: {ve}")
        return None, desc

    except re.error as re_err:
        print(f"Regex error: {re_err}")
        return None, desc

    except TypeError as type_err:
        print(f"Type error: {type_err}")
        return None, desc


def download_image(image_url):
    """Downloads an image from a given URL and saves it in the output/images directory."""
    fs = FileSystem()
    save_directory = "output/images"
    fs.create_directory(save_directory)

    image_filename = f"{uuid.uuid4()}.jpg"
    image_path = f"{save_directory}/{image_filename}"

    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            fs.create_binary_file(image_path, response.content)
            print(f"Image saved as {image_path}")
        else:
            print("Failed to download image.")
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")

    return image_filename


def count_search_phrases(art_title, art_description, search_phrase):
    """Counts occurrences of the search phrase in the article title and description."""
    search_phrase = search_phrase.lower()
    art_title = art_title.lower()
    art_description = art_description.lower()

    count_in_title = art_title.count(search_phrase)
    count_in_description = art_description.count(search_phrase)
    total_count = count_in_title + count_in_description

    return total_count


def contains_money(art_title, art_description):
    """Checks if the title or description contains any monetary values."""
    money_pattern = r'\$\d{1,3}(,\d{3})*(\.\d{2})?|\d+\s?(dollars|usd)'

    art_title = art_title.lower()
    art_description = art_description.lower()

    return bool(re.search(money_pattern, art_title) or re.search(money_pattern, art_description))


def save_to_excel(data, headers, directory="output"):
    """Saves the given data to an Excel file with a unique name based on the current timestamp."""
    excel = Files()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{directory}/news_data_{timestamp}.xlsx"
    excel.create_workbook(file_name)
    excel.append_rows_to_worksheet([headers])
    excel.append_rows_to_worksheet(data)
    excel.save_workbook()
    excel.close_workbook()
    print(f"Data saved to {file_name}")


def is_within_date_range(article_date, months):
    """Check if the article date is within the specified range of months."""
    current_date = datetime.now()
    date_limit = current_date - timedelta(days=30 * months)
    article_datetime = datetime.strptime(article_date, '%d-%m-%Y')
    return article_datetime >= date_limit


def click_show_more_button():
    """Clicks the 'Show More' button if it is present."""
    try:
        browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
        show_more_button_xpath = "//button[@data-testid='show-more-button']"
        if browser.is_element_visible(show_more_button_xpath):
            browser.click_button(show_more_button_xpath)
            browser.wait_until_element_is_not_visible(show_more_button_xpath, timeout=10)
            print("Clicked 'Show More' and loaded more results.")
            return True
    except Exception as e:
        print(f"Error clicking 'Show More': {e}")
    return False


def process_articles_within_date_range(search_text, number_of_months):
    """Process and save articles within the specified date range."""
    headers = ["Title", "Date", "Description", "Image Filename",
               "Search Phrase Occurrences", "Contains Money"]
    data = []

    article_index = 1
    while True:  # Continue processing until no more articles are found
        try:
            title_xpath = f"(//h3[@class='gc__title']/a)[{article_index}]"
            description_xpath = f"(//article//p)[{article_index}]"
            img_xpath = f"(//article//img)[{article_index}]"

            try:
                # Attempt to wait for the title element to be present on the page
                browser.wait_until_page_contains_element(title_xpath, timeout=5)
            except Exception:
                # If the element is not found, attempt to load more articles
                if not click_show_more_button():
                    print("No more articles to load.")
                    break  # Exit the loop if no more articles can be loaded
                continue  # Retry after loading more articles

            # Proceed if the element is visible
            title = browser.get_text(title_xpath)
            date_and_description = browser.get_text(description_xpath)
            unparsed_date, description = extract_date_and_clean_description(
                date_and_description)
            article_date = parse_aljazeera_date(unparsed_date)

            if not article_date:
                print(f"Article {article_index}: Failed to parse date.")
                article_index += 1
                continue

            print(f"Article {article_index}: Date parsed as {article_date}.")

            if not is_within_date_range(article_date, number_of_months):
                print(f"Article {article_index}: Outside the date range.")
                article_index += 1
                continue

            img_visible = browser.is_element_visible(img_xpath)
            if img_visible:
                img_url = browser.get_element_attribute(f"xpath:{img_xpath}", "src")
                downloaded_image = download_image(img_url)
            else:
                downloaded_image = ""

            total_occurrences = count_search_phrases(
                title, description, search_text)
            has_money = contains_money(title, description)

            data.append([title, article_date, description,
                        downloaded_image, total_occurrences, has_money])

        except Exception as e:
            print(f"Error processing article {article_index}: {e}")

        article_index += 1

    if data:
        save_to_excel(data, headers)
    else:
        print("No articles were saved.")


# Example usage in your main script
URL = "https://www.aljazeera.com/"
SEARCH_TEXT = "investment"
CATEGORY = "Date"
NUMBER_OF_MONTHS = 2  # Example: process articles from the current and previous month

browser = Selenium()
browser.open_available_browser(URL, maximized=True)
browser.click_element("xpath://button[@type='button']")
browser.input_text("xpath://input[@placeholder='Search']", SEARCH_TEXT)
browser.press_key("xpath://input[@placeholder='Search']", Keys.ENTER)
browser.click_element_when_visible("id:search-sort-option")
browser.click_element_when_visible(
    f"xpath://option[@value='{CATEGORY.lower()}']")

process_articles_within_date_range(SEARCH_TEXT, NUMBER_OF_MONTHS)

browser.close_all_browsers()
