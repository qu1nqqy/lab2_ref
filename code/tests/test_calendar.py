# tests/test_calendar.py

import pytest
from code.mycalendar import MyCalendar
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


@pytest.fixture
def calendar_instance():
    """Фикстура: пустой календарь без событий"""
    return MyCalendar(username="testuser", linked_date={})


def test_format_month_returns_valid_html_table(calendar_instance):
    """Проверка: метод formatmonth возвращает HTML-таблицу"""
    html = calendar_instance.formatmonth(2025, 3)
    soup = BeautifulSoup(html, "html.parser")
    assert soup.find("table") is not None
    assert "2025" in html


def test_formatday_no_event(calendar_instance):
    """Проверка: день без события — нет подсветки"""
    html = calendar_instance.formatday(10, 0, 2025, 3)
    assert "has-background" not in html
    assert "todo/testuser/2025/3/10" in html


def test_formatday_with_finished_event():
    """Проверка: завершённое событие выделяется зелёным"""
    linked = {"20250315": True}
    calendar = MyCalendar(username="testuser", linked_date=linked)
    html = calendar.formatday(15, 0, 2025, 3)
    assert "has-background-success" in html
    assert "has-text-white" in html


def test_formatday_with_upcoming_event():
    """Проверка: будущее событие выделяется жёлтым"""
    future = datetime.now() + timedelta(days=3)
    date_str = future.strftime("%Y%m%d")
    linked = {date_str: False}
    calendar = MyCalendar(username="testuser", linked_date=linked)
    html = calendar.formatday(future.day, future.weekday(), future.year, future.month)
    assert "has-background-warning" in html


def test_formatday_today_highlighted():
    """Проверка: текущий день выделяется синим"""
    today = datetime.today()
    date_str = today.strftime("%Y%m%d")
    calendar = MyCalendar(username="testuser", linked_date={})
    html = calendar.formatday(today.day, today.weekday(), today.year, today.month)
    assert "has-background-primary" in html
    assert "has-text-weight-bold" in html
