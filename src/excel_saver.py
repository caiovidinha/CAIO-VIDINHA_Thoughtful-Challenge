from RPA.Excel.Files import Files
from datetime import datetime

class ExcelSaver:
    def __init__(self, directory="output"):
        self.directory = directory
        self.excel = Files()

    def save(self, articles, headers):
        """Saves the given articles to an Excel file with a unique name."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{self.directory}/news_data_{timestamp}.xlsx"
        self.excel.create_workbook(file_name)
        self.excel.append_rows_to_worksheet([headers])
        
        for article in articles:
            self.excel.append_rows_to_worksheet([article])

        self.excel.save_workbook()
        self.excel.close_workbook()
