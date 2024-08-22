import re
from src.date_parser import DateParser  
from src.text_analyzer import TextAnalyzer  

class Article:
    def __init__(self, title, description, unparsed_date, image_url=None):
        self.title = title
        self.description = description
        self.image_url = image_url
        self.image_filename = None
        self.date = DateParser.parse_aljazeera_date(unparsed_date)

    @staticmethod
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

    def download_image(self, downloader):
        """Downloads the article's image using the provided downloader."""
        if self.image_url:
            self.image_filename = downloader.download_image(self.image_url)

    def count_search_phrases(self, search_phrase):
        """Counts occurrences of the search phrase in the title and description."""
        return TextAnalyzer.count_search_phrases(self.title, search_phrase) + \
               TextAnalyzer.count_search_phrases(self.description, search_phrase)

    def contains_money(self):
        """Checks if the title or description contains any monetary values."""
        return TextAnalyzer.contains_money(self.title) or \
               TextAnalyzer.contains_money(self.description)

    def to_list(self, search_phrase_occurrences, contains_money):
        """Returns the article data as a list for easy saving to Excel."""
        return [self.title, self.date, self.description, self.image_filename, search_phrase_occurrences, contains_money]
