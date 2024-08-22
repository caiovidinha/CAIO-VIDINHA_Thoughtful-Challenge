import re

class TextAnalyzer:
    @staticmethod
    def count_search_phrases(text, search_phrase):
        """Counts occurrences of the search phrase in the given text."""
        search_phrase = search_phrase.lower()
        text = text.lower()
        return text.count(search_phrase)

    @staticmethod
    def contains_money(text):
        """Checks if the text contains any monetary values."""
        money_pattern = r'\$\d{1,3}(,\d{3})*(\.\d{2})?|\d+\s?(dollars|usd)'
        text = text.lower()
        return bool(re.search(money_pattern, text))
