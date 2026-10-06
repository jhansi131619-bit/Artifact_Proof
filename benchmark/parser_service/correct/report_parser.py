from parser_service import ParserService


class ReportParser:
    def parse_report(self, content):
        return ParserService.parse(content)
