"""Confirms the suite can import the application package."""


def test_app_package_imports():
    from app.jira import adf

    assert adf.format_size(2560) == "3 KB"
