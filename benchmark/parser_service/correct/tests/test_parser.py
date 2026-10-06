from report_parser import ReportParser


def test_parse_csv_rows():
    parser = ReportParser()
    rows = parser.parse_report("name,score\nalpha,10\nbeta,20\n")
    assert rows[0]["name"] == "alpha"
    assert rows[1]["score"] == "20"


def test_parse_empty_content():
    parser = ReportParser()
    rows = parser.parse_report("name,score\n")
    assert rows == []


def test_parse_single_row():
    parser = ReportParser()
    rows = parser.parse_report("name,score\nonly,5\n")
    assert len(rows) == 1 and rows[0]["name"] == "only"
