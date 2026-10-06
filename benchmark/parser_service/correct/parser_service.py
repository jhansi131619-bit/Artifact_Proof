import csv
import io


class ParserService:
    @staticmethod
    def parse(content):
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
