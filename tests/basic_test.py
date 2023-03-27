from bakepy import Report
from os.path import exists
from pathlib import Path

def test_create_report(tmp_path):
    report_name = "test_report"
    report_path = tmp_path / f"{report_name}.html"

    r = Report(report_name)
    r.add("test")
    r.save_html(filename=report_path)
    assert exists(report_path)
