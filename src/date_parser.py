import re
from datetime import datetime, timedelta
from dateutil import parser

class DateParser:
    @staticmethod
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

    @staticmethod
    def is_within_date_range(article_date, months):
        """Check if the article date is within the specified range of months."""
        current_date = datetime.now()
        date_limit = current_date - timedelta(days=30 * months)
        article_datetime = datetime.strptime(article_date, '%d-%m-%Y')
        return article_datetime >= date_limit
