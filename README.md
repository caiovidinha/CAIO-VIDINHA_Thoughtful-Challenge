# Thoughtful RPA Coding Challenge - Extracting data from a news site.

This project documents the journey of developing an automation bot to scrape articles from [Al Jazeera](https://www.aljazeera.com/) using Python and Selenium within the RPAframework. This README captures the thought process, challenges, and solutions implemented during the project.

---

## Understanding the Challenge

The first step in this project was to thoroughly read and understand the challenge provided. I took detailed notes on areas that were unclear and performed extensive research to familiarize myself with the necessary terms and technologies. This foundational step was crucial in building a solid understanding before proceeding with development.

---

## Phase 1: Planning and Setup

### Choosing the Site

After careful consideration, I chose [Al Jazeera](https://www.aljazeera.com/) as the target site for scraping articles. The decision was based on the site's consistent structure, relevance, and the diversity of content that would allow for comprehensive testing of the scraper.

### Creating the Environment

After some trial and error, I determined that Python 3.10.12 was the most suitable environment for this project. The setup was crucial for ensuring compatibility with the necessary libraries and tools.

### Initial Implementation

The goal at this stage was to create a simple, functional script that could scrape the first article on the page. This initial implementation was crucial for building the foundation that the more complex aspects of the project would be built on. The process included:

-   **Basic Functionality:** Writing code to access the website, perform a search, and extract data for the first article.
-   **No POO/Work Items Yet:** At this stage, I focused solely on getting the basic scraping functionality working. The code was kept simple, without the use of object-oriented programming or Robocorp Work Items, to facilitate rapid iteration and testing.

Here’s a snippet of the initial implementation:

```python
from RPA.Browser.Selenium import Selenium

browser = Selenium()

browser.open_available_browser("https://www.aljazeera.com/", maximized=True)
browser.input_text("xpath://input[@placeholder='Search']", "science")
browser.press_keys("xpath://input[@placeholder='Search']", "ENTER")

title = browser.get_text("xpath://h3[@class='gc__title']/a")
date_and_description = browser.get_text("xpath:(//article//p)[1]")

print(f"Title: {title}")
print(f"Date and Description: {date_and_description}")

browser.close_all_browsers()
```

---

## Phase 2: Solving Key Challenges

### XPath Identification

One of the early challenges was identifying the correct XPath for the elements I needed to scrape. Al Jazeera’s website has multiple layers, which made it difficult to pinpoint the exact paths. Here’s how I tackled this:

-   **Using "Selector Gadget":** I used the Selector Gadget browser extension to highlight and select the desired elements on the page. This tool was invaluable for generating accurate XPaths.
-   **Manual Inspection:** In cases where Selector Gadget wasn’t sufficient, I manually inspected elements using the browser’s developer tools. This involved hiding certain elements and revealing others to understand the structure.

### Category Selection

The site had a dropdown filter to sort the articles by relevance or date. I decided to implement functionality to select this filter based on a category variable. Here’s how the code looked:

```python
category = "Date"
browser.click_element_when_visible("id:search-sort-option")
browser.click_element_when_visible(f"xpath://option[@value='{category.lower()}']")
```

### Date Parsing

Parsing the date was one of the more complex tasks due to the various formats used on the site. Articles had dates in relative formats (e.g., "3 days ago") or absolute formats (e.g., "Aug 12, 2024"). I wrote the parse_aljazeera_date function to handle this:

-   **Relative Date Identification:** The function identifies if the date is relative by looking for keywords like "days", "hours", etc.
-   **Absolute Date Parsing:** If the date is absolute, the function parses it directly.
-   **Error Handling:** The function raises an error if the date format is not recognized.
    Here’s the code for the function:

```python
import re
from datetime import datetime, timedelta
from dateutil import parser

def parse_aljazeera_date(date_str):
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
        parsed_date = datetime.now() - delta
    else:
        try:
            parsed_date = parser.parse(date_str)
        except (ValueError, OverflowError):
            return None

    return parsed_date.strftime('%d-%m-%Y')
```

### Description Cleaning

Next, I focused on cleaning up the article descriptions. The challenge was to remove dates from the descriptions and handle cases where descriptions started with "..." or other non-letter characters. The solution involved:

-   **Regular Expressions:** To identify and remove dates.
-   **Text Cleaning:** To strip out leading "..." and ensure descriptions started with a letter.

Here’s the function that handles this:

```python
import re

def extract_date_and_clean_description(description):
    try:
        relative_pattern = r'\d+\s+(minute|minutes?|hour|hours?|day|days?)\s+ago'
        absolute_pattern = r'[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}'
        full_pattern = f'({relative_pattern})|({absolute_pattern})'

        date_match = re.search(full_pattern, description)
        if not date_match:
            raise ValueError("No date found in description.")

        date_str = date_match.group(0)
        cleaned_description = re.sub(full_pattern, '', description).strip()
        cleaned_description = re.sub(r'^\.{3}', '', cleaned_description).strip()

        if not cleaned_description:
            raise ValueError("Description is empty after cleaning.")

        return date_str, cleaned_description

    except ValueError as ve:
        print(f"Error: {ve}")
        return None, description

```

### Image Handling

Handling images was relatively straightforward:

-   **Identify the 'src' Attribute:** The image URL was extracted from the 'src' attribute of the 'img' tag.

Here's how the function looked:

```python
from RPA.FileSystem import FileSystem
import requests
import uuid

def download_image(image_url):
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
```

### Counting Search Phrase Occurrences

The next task was to count the occurrences of the search phrase in both the title and description of each article. I ensured that the search was case-insensitive and handled edge cases, such as variations in monetary amounts.

```python
def count_search_phrases(title, description, search_phrase):
    search_phrase = search_phrase.lower()
    title = title.lower()
    description = description.lower()

    count_in_title = title.count(search_phrase)
    count_in_description = description.count(search_phrase)
    total_count = count_in_title + count_in_description

    return total_count
```

### Identifying money and currency

To develop the contains_money function, I focused on identifying and handling various formats in which monetary values might appear in the title or description of an article. The challenge was to create a robust solution that could accurately detect different representations of money, including those with various currencies and formats.

#### Approach:

1. **Regular Expression Design:**

-   I began by designing a regular expression that could match common monetary patterns. This included formats such as:
    -   Standard dollar amounts like $11.1, $111,111.11.
    -   Numeric values followed by currency names or symbols, such as 11 dollars, 11 USD.
-   The goal was to cover as many realistic scenarios as possible, ensuring the regex was comprehensive yet efficient.

2. **Case Insensitivity:**

-   To ensure that the detection was not case-sensitive, I converted both the title and description to lowercase before applying the regular expression. This allowed for a more flexible search, catching all variations regardless of capitalization.

3. **Pattern Matching:**

-   The function then searched through the title and description using the defined regex. If a match was found, the function would return True, indicating the presence of monetary values. If no match was found, it would return False.

#### Implementation:

```python
import re

def contains_money(title, description):
    """Checks if the title or description contains any monetary values."""
    money_pattern = r'\$\d{1,3}(,\d{3})*(\.\d{2})?|\d+\s?(dollars|usd)'

    title = title.lower()
    description = description.lower()

    return bool(re.search(money_pattern, title) or re.search(money_pattern, description))
```

---

## Phase 3: Enhancing the Solution

### Implementing Excel Output

After successfully scraping the article data, the next step was to save this data in a structured format. I chose Excel as the output format due to its widespread use and ability to handle tabular data effectively.

#### Steps to Implement Excel Output:

1. Choosing the Library:
   I opted to use the RPA.Excel.Files module from rpaframework, which integrates seamlessly into the Robocorp environment and supports creating and manipulating Excel files.

2. Creating the Excel File:
   The file name was dynamically generated based on the timestamp of the run, ensuring that each execution produced a unique output file. The headers were set up to organize the data into columns.

3. Saving the Data:
   I appended rows of data to the Excel file and ensured that it was saved in the output directory of the Robocorp environment.

Here’s how the function was implemented:

```python
from RPA.Excel.Files import Files
from datetime import datetime
from pathlib import Path

    def save( data, headers, directory="output"):
        excel = Files()
        Path(directory).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{directory}/news_data_{timestamp}.xlsx"

        excel.create_workbook(file_name)
        excel.append_rows_to_worksheet([headers])
        excel.append_rows_to_worksheet(data)
        excel.save_workbook()
        excel.close_workbook()
        print(f"Data saved to {file_name}")
```

### Iterating Over All Articles

Once I had the basic functionality working for a single article, the next step was to expand it to iterate over all articles on the page. This involved:

-   Looping Through Articles: I set up a loop to go through each article on the page, extracting the required information.
-   Filtering by Date: Using the 'number_of_months' parameter, I filtered articles to ensure that only those within the specified date range were processed.

### Handling "Show More"

The site only renders 10 articles initially, requiring a click on a "Show More" button to load additional articles. To handle this:

-   Scroll and Click: I implemented logic to scroll to the bottom of the page and click the "Show More" button until all articles were loaded.
-   Explicit Waits: Added waits to ensure that elements were loaded before attempting to interact with them.

Here’s how this functionality was implemented:

```python
def click_show_more_button(browser):
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
```

---

## Phase 4: Refactoring to OOP

### Approach to OOP Refactoring

Once the basic functionality was in place and working, the next step was to refactor the code into an object-oriented structure. This refactoring aimed to make the code more modular, maintainable, and easier to extend.

### Key Steps in Refactoring:

**1. Identifying Core Components:**
I started by identifying the main components of the script that could be encapsulated into classes. These included the scraper logic, article data handling, and Excel output.

**2. Creating Classes:**

**ArticleScraper (article_scraper.py)**:

-   **Purpose**: Responsible for orchestrating the scraping process, from navigating the website, extracting data, to interacting with the user interface.
-   **Main Tasks**: Set up the browser, search for articles, apply filters, and iterate through available articles to collect relevant information.

**Article (article.py)**:

-   **Purpose**: Represents a single article, encapsulating data related to it, such as title, date, description, image, and additional information (like monetary values and search phrase counts).
-   **Main Tasks**: Store and process data extracted from each individual article.
    **DateParser (date_parser.py)**:
-   **Purpose**: Handles the extraction and formatting of dates, particularly identifying and converting relative and absolute dates found in articles.
-   **Main Tasks**: Parse date strings in various formats and convert them to a standardized format.

**ExcelSaver (excel_saver.py)**:

-   **Purpose**: Manages the saving of extracted data into an Excel file, ensuring that the information is organized and stored correctly.
-   **Main Tasks**: Create the Excel file, set up headers, append data, and save the file to the appropriate directory structure.

**ImageDownloader (image_downloader.py)**:

-   **Purpose**: Responsible for downloading images from provided URLs and saving these images locally.
-   **Main Tasks**: Download the image from a URL, generate a unique file name, and save the image in a specified directory.
    **TextAnalyzer (text_analyzer.py)**:
-   **Purpose**: Performs text analysis, such as counting occurrences of search phrases and detecting monetary values in the descriptions and titles of articles.
-   **Main Tasks**: Analyze texts to identify specific patterns, such as monetary values, and count how many times a search phrase appears.

**3. Encapsulation and Modularization:**

-   Each class was responsible for a specific aspect of the scraping process. This separation of concerns made the code more modular and allowed for easier testing and debugging.
-   For example, the **'ArticleScraper'** class handled the flow of the scraping process, while the **'Article'** class focused on processing and storing data related to individual articles.

**4. Improving Reusability:**

-   By breaking down the functionality into classes and methods, I improved the reusability of the code. For example, the Article class could be reused or extended to handle different types of articles or websites in the future.

Here’s an example of how the refactoring was implemented:

```python
class ArticleScraper:
    def __init__(self, url, search_text, category, number_of_months):
        self.url = url
        self.search_text = search_text
        self.category = category
        self.number_of_months = number_of_months
        self.browser = Selenium()

    def scrape(self):
        self.browser.open_available_browser(self.url, maximized=True)
        self.browser.input_text("xpath://input[@placeholder='Search']", self.search_text)
        self.browser.press_keys("xpath://input[@placeholder='Search']", Keys.ENTER)
        self.browser.click_element_when_visible(f"xpath://option[@value='{self.category.lower()}']")

        # Process articles within the specified date range
        self.process_articles_within_date_range()

    def process_articles_within_date_range(self):
        # Implementation for processing articles
        pass

    def __del__(self):
        self.browser.close_all_browsers()
```

---

## Phase 5: Final Configurations

### Replacing variables with Work Items

With some research and previous experiences, I implemented inputs via Work Items. I also dealt with "bad inputs" at this point, so these "trycatch" statements solve that.

-   _Obs.: Also, some logging spoiler at the code, sorry._
-   Here’s the code:

```python
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
```
### Adding Loggig
To make the script more robust and easier to debug, I added logging throughout the code. 
This provided visibility into the script’s execution flow and helped in identifying issues during development and testing.
I imported and configures logging to log into a file and input, and replaced all the "prints" I had with "logging", also, I went through the whole proccess trying to add logs to follow the best practices.
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
```

### Setting Up `robot.yaml`, `conda.yaml`, and @task

To integrate the script into the Robocorp platform, I needed to configure the environment files and tasks.

1. **`robot.yaml`**:

    - This file was used to define the tasks that would be executed. The `@task` decorator was applied to the main function to designate it as the entry point for the automation.

2. **`conda.yaml`**:

    - Managed the dependencies for the project. By specifying the exact Python version and libraries needed, I ensured consistency across different environments.

### Ensuring PEP8 Compliance

Finally, I ensured that the code adhered to PEP8 standards. This included organizing imports, managing line lengths, and adding necessary docstrings for functions and classes. (With some help of PEP8 documentation and pylint)

---

## Phase 6: Deployment and Testing

### Publishing to GitHub

The completed project was published to GitHub. This included the entire project structure, including the robot.yaml and conda.yaml files, which are necessary for running the automation in the Robocorp environment.

### Configuring Robocorp and Work Items

After publishing, the next step was to set up the automation in Robocorp. This involved creating a new robot in the Robocorp Control Room and configuring Work Items for input and output data handling.

### Running, Testing, and Enhancing

With everything set up, I ran the automation in Robocorp, monitored the logs, and made any necessary adjustments. This iterative process ensured that the bot was reliable and could handle different scenarios and edge cases.

---

## Conclusion

### Handling Bad Inputs and Success

One of the final steps in this project was implementing robust error handling to manage bad inputs gracefully. This ensured that the automation process would not fail unexpectedly and could provide meaningful feedback in case of errors. By focusing on this, the bot became more resilient, capable of running under various conditions while maintaining reliability.

The project demonstrates the importance of:

-   **Planning and Research**: Thoroughly understanding the challenge and researching necessary technologies is crucial before starting the development.
-   **Iterative Development**: Starting with a simple solution and progressively enhancing it with more features and robustness.
-   **Modular and Maintainable Code**: Refactoring the script into a well-structured, object-oriented design helped in managing complexity and enhancing reusability.
-   **Integration with Robocorp**: Replacing static variables with Work Items and configuring the environment correctly ensured that the bot could be deployed and run smoothly in the Robocorp ecosystem.
-   **Testing and Debugging**: Continuous testing and debugging were essential to refining the bot's performance and ensuring it handled edge cases effectively.

---

### Acknowledgement

I would like to express my gratitude to Thoughtful for the opportunity to participate in this process. I am excited about the prospect of working with the Thoughtful team in the future. I look forward to the possibility of contributing to your innovative projects and making a meaningful impact together.
