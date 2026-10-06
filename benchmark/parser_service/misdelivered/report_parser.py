import csv
import io


class ReportParser:
    def parse_report(self, content):
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)
