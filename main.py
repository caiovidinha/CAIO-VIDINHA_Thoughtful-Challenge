"""
This module initializes and runs the article scraping process using Robocorp Work Items.
"""

import logging
from robocorp.tasks import task
from RPA.Robocorp.WorkItems import WorkItems
from src.article_scraper import ArticleScraper

@task
def main():
    """Main function to execute the scraping process using Robocorp Work Items."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("scraper.log"),
            logging.StreamHandler()
        ]
    )

    work_items = WorkItems()
    work_items.get_input_work_item()

    try:
        url = work_items.get_work_item_variable("url")
        if not url:
            raise ValueError("Missing 'url' in Work Items.")
    except Exception as e:
        logging.error(f"Error retrieving 'url': {e}")
        raise

    try:
        search_text = work_items.get_work_item_variable("search_text")
        if not search_text:
            raise ValueError("Missing 'search_text' in Work Items.")
    except Exception as e:
        logging.error(f"Error retrieving 'search_text': {e}")
        raise

    try:
        category = work_items.get_work_item_variable("category")
    except Exception as e:
        logging.warning(f"Error retrieving 'category': {e}. Defaulting to 'relevance'.")
        category = 'relevance'

    try:
        number_of_months = int(work_items.get_work_item_variable("number_of_months") or 0)
    except Exception as e:
        logging.warning(f"Error retrieving 'number_of_months': {e}. Defaulting to '0'.")
        number_of_months = 0

    logging.info("Work Item Variables - URL: %s, Search Text: %s, Category: %s, Number of Months: %s",
                 url, search_text, category, number_of_months)

    scraper = ArticleScraper(url, search_text, category, number_of_months)
    scraper.scrape()

    work_items.create_output_work_item()
    work_items.save_work_item()
    logging.info("Work item output saved successfully.")

if __name__ == "__main__":
    main()