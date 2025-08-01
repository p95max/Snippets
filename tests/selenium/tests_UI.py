import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By


@pytest.mark.django_db
def test_view_snippets_button_on_homepage(browser, live_server):
    """
    Тест проверяет, что на главной странице есть ссылка с текстом 'Общие сниппеты',
    которая ведет на url с именем 'MainApp:snippets-list'
    """
    # Открываем главную страницу
    browser.get(f"{live_server.url}/")

    # Ищем ссылку с текстом, содержащим 'Общие сниппеты'
    view_snippets_link = browser.find_element(
        By.XPATH, "//a[strong[contains(text(), 'Общие сниппеты')]]"
    )

    # Проверяем, что ссылка найдена
    assert view_snippets_link is not None

    # Проверяем, что ссылка ведет на правильный URL (MainApp:snippets-list)
    expected_url = f"{live_server.url}{reverse('MainApp:snippets-list')}"
    actual_href = view_snippets_link.get_attribute('href')

    assert actual_href == expected_url, f"Ожидался URL: {expected_url}, получен: {actual_href}"
