import time

from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from django.urls import reverse
import pytest
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from tests.factories import UserFactory, SnippetFactory


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


# task 1

@pytest.mark.django_db
def test_navigation_buttons_for_unauthorized_user(browser, live_server):
    # Открываем главную страницу
    browser.get(f"{live_server.url}{reverse('MainApp:home')}")

    # Кликаем по кнопке "гамбургер", чтобы раскрыть меню (если свернуто)
    toggler = browser.find_element(By.CLASS_NAME, "navbar-toggler")
    toggler.click()

    # Проверяем, что кнопка "Общие сниппеты" доступна
    view_snippets_button = browser.find_element(By.XPATH, "//a[strong[contains(text(), 'Общие сниппеты')]]")
    expected_url = f"{live_server.url}{reverse('MainApp:snippets-list')}"
    actual_href = view_snippets_button.get_attribute('href')
    assert actual_href == expected_url, f"Ожидался URL: {expected_url}, получен: {actual_href}"
    assert view_snippets_button.is_displayed()
    assert view_snippets_button.is_enabled()

    # Проверяем кнопку "Регистрация"
    registration_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Регистрация')]")
    expected_url = f"{live_server.url}{reverse('MainApp:custom_regist')}"
    actual_href = registration_button.get_attribute('href')
    assert actual_href == expected_url, f"Ожидался URL: {expected_url}, получен: {actual_href}"
    registration_button = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//a[contains(text(), 'Регистрация')]"))
    )
    assert registration_button.is_displayed()
    assert registration_button.is_enabled()

    # Проверяем, что кнопка "Мои сниппеты" отсутствует
    my_snippets_buttons = browser.find_elements(By.XPATH, "//a[strong[contains(text(), 'Мои сниппеты')]]")
    assert len(my_snippets_buttons) == 0, "Кнопка 'Мои сниппеты' не должна быть доступна для неавторизованного пользователя"



@pytest.mark.django_db
def test_navigation_buttons_for_authorized_user(browser, live_server):
    """
    Тест проверяет, что для авторизованного пользователя в header доступны:
    - кнопка "Посмотреть сниппеты"
    - кнопка "Мои сниппеты"
    Но недоступна кнопка "Регистрация"
    """
    # Устанавливаем размер окна браузера, чтобы избежать проблем с мобильной версией
    browser.set_window_size(1920, 1080)

    # Создаем пользователя
    user = UserFactory(username="testuser")
    user.set_password("defaultpassword")  # Устанавливаем пароль явно
    user.save()

    # Очищаем куки и выполняем logout для чистого состояния
    browser.delete_all_cookies()
    browser.get(f"{live_server.url}/logout/")  # Используем /logout/ из urls.py
    print(f"URL после logout: {browser.current_url}")

    # Ждем полной загрузки страницы после logout
    WebDriverWait(browser, 10).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

    # Переходим на главную страницу
    browser.get(f"{live_server.url}{reverse('MainApp:home')}")
    print(f"URL главной страницы: {browser.current_url}")

    # Ждем полной загрузки главной страницы
    WebDriverWait(browser, 10).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )

    # Проверяем, свернуто ли меню (для мобильной версии)
    try:
        toggler = browser.find_element(By.CLASS_NAME, "navbar-toggler")
        if toggler.is_displayed():
            print("Меню свернуто, раскрываем...")
            toggler.click()
            WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.ID, "navbarContent"))
            )
            print("Меню раскрыто")
    except:
        print("Кнопка toggler не найдена или не нужна")

    # Проверяем наличие формы логина
    try:
        form = WebDriverWait(browser, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//form[contains(@action, 'custom_login')]"))
        )
        print("Форма логина найдена")
    except:
        print(f"Ошибка: Форма логина не найдена. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_login_form.png")
        raise

    # Ждем появления поля username
    try:
        username_input = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))
        )
        print("Поле username найдено и кликабельно")
    except:
        print(f"Ошибка: Поле username не найдено или не кликабельно. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_username_field.png")
        raise

    # Заполняем форму авторизации
    password_input = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
    )

    username_input.clear()
    username_input.send_keys(user.username)
    password_input.clear()
    password_input.send_keys("defaultpassword")

    # Отправляем форму
    login_button = WebDriverWait(browser, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_button.click()

    # Ждем перенаправления на главную страницу
    try:
        WebDriverWait(browser, 20).until(
            EC.url_contains(reverse('MainApp:home'))
        )
        print(f"Редирект после логина успешен: {browser.current_url}")
    except:
        print(f"Ошибка: Не удалось подтвердить редирект после логина. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_post_login.png")
        raise

    # Проверяем, что кнопка "Посмотреть сниппеты" доступна
    view_snippets_button = WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "Общие сниппеты"))
    )
    assert view_snippets_button.is_displayed()
    assert view_snippets_button.is_enabled()

    # Проверяем, что кнопка "Мои сниппеты" доступна
    my_snippets_button = WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "Мои сниппеты"))
    )
    assert my_snippets_button.is_displayed()
    assert my_snippets_button.is_enabled()

    # Проверяем, что кнопка "Регистрация" НЕ доступна (не должна быть видна)
    registration_buttons = browser.find_elements(By.PARTIAL_LINK_TEXT, "Регистрация")
    assert len(
        registration_buttons) == 0, "Кнопка 'Регистрация' не должна быть доступна для авторизованного пользователя"

    # Дополнительно проверяем, что отображается приветствие пользователя
    welcome_text = WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Добро пожаловать')]"))
    )
    assert welcome_text.is_displayed()

    # Проверяем наличие ссылки "Выйти"
    logout_link = WebDriverWait(browser, 20).until(
        EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "Выйти"))
    )
    assert logout_link.is_displayed()
    assert logout_link.is_enabled()


# task 2

@pytest.mark.django_db
def test_snippets_my_page_access_and_content(browser, live_server):
    """
    Тест проверяет страницу 'Мои сниппеты':
    1. По url может пройти только авторизованный пользователь
    2. На странице доступны только сниппеты авторизованного пользователя
    """
    # Создаем двух пользователей
    user1 = UserFactory()
    user2 = UserFactory()

    # Создаем сниппеты для каждого пользователя
    user1_snippets = SnippetFactory.create_batch(3, user=user1, public=True)
    user2_snippets = SnippetFactory.create_batch(2, user=user2, public=True)

    # Тест 1: Проверяем, что неавторизованный пользователь не может получить доступ
    try:
        browser.get(f"{live_server.url}{reverse('MainApp:user_snippets')}")
        page_content = browser.find_element(By.TAG_NAME, "body").text
        assert "Мои сниппеты" not in page_content, \
            "Неавторизованный пользователь не должен иметь доступ к странице 'Мои сниппеты'"
    except Exception as e:
        assert "403" in str(e) or "Permission" in str(e) or "Forbidden" in str(e), \
            f"Ожидалась ошибка доступа, получена: {e}"

    # Тест 2: Проверяем доступ для авторизованного пользователя
    browser.get(f"{live_server.url}{reverse('MainApp:home')}")

    # Проверяем, свернуто ли меню (для мобильной версии)
    try:
        toggler = browser.find_element(By.CLASS_NAME, "navbar-toggler")
        if toggler.is_displayed():
            toggler.click()
            WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.ID, "navbarContent"))
            )
    except:
        pass

    # Ждем появления формы авторизации
    try:
        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
    except:
        print(f"Ошибка: Форма логина не найдена. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_login_form.png")
        raise

    # Заполняем форму авторизации для user1
    username_input = browser.find_element(By.CSS_SELECTOR, "input[name='username']")
    password_input = browser.find_element(By.CSS_SELECTOR, "input[name='password']")
    csrf_input = browser.find_element(By.CSS_SELECTOR, "input[name='csrfmiddlewaretoken']")

    username_input.send_keys(user1.username)
    password_input.send_keys("defaultpassword")

    # Отправляем форму
    login_form = browser.find_element(By.CSS_SELECTOR, "form[action*='custom_login']")
    browser.execute_script("arguments[0].submit();", login_form)

    # Ждем перенаправления на главную страницу
    try:
        WebDriverWait(browser, 10).until(
            EC.url_to_be(f"{live_server.url}{reverse('MainApp:home')}")
        )
    except:
        print(f"Ошибка: Не удалось подтвердить редирект после логина. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_post_login.png")
        raise

    # Проверяем, что пользователь авторизован (появляется приветственное сообщение)
    try:
        # Снова раскрываем меню, если оно свернуто
        try:
            toggler = browser.find_element(By.CLASS_NAME, "navbar-toggler")
            if toggler.is_displayed():
                toggler.click()
                WebDriverWait(browser, 5).until(
                    EC.visibility_of_element_located((By.ID, "navbarContent"))
                )
        except:
            pass

        navbar_text = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.navbar-text.me-3"))
        )
        welcome_span = navbar_text.find_element(By.CSS_SELECTOR, "span[style*='color:#56d364']")
        assert welcome_span.text == user1.username, \
            f"В приветствии должен быть username {user1.username}, а не '{welcome_span.text}'"
    except:
        print(f"Ошибка: Приветственное сообщение не найдено. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_welcome_message.png")
        raise

    # Теперь переходим на страницу "Мои сниппеты"
    browser.get(f"{live_server.url}{reverse('MainApp:user_snippets')}")

    # Проверяем, что мы успешно перешли на страницу
    current_url = browser.current_url
    assert current_url == f"{live_server.url}{reverse('MainApp:user_snippets')}", \
        f"Авторизованный пользователь должен иметь доступ к странице 'Мои сниппеты'. Текущий URL: {current_url}"

    # Проверяем содержимое страницы
    page_content = browser.find_element(By.TAG_NAME, "body").text
    assert user1.username in page_content, \
        f"Текст страницы должен содержать имя пользователя {user1.username}, получен: {page_content}"

    # Проверяем наличие кнопки "Добавить сниппет" (подтверждает авторизацию)
    try:
        add_snippet_button = browser.find_element(By.XPATH, "//a[contains(text(), 'Добавить сниппет')]")
        assert add_snippet_button.is_displayed(), \
            "Кнопка 'Добавить сниппет' должна быть видна для авторизованного пользователя"
    except:
        print(f"Ошибка: Кнопка 'Добавить сниппет' не найдена. Текущий URL: {browser.current_url}")
        print(f"HTML страницы:\n{browser.page_source}")
        browser.save_screenshot("error_add_snippet_button.png")
        raise

    # Тест 3: Проверяем, что отображаются только сниппеты авторизованного пользователя
    snippet_rows = browser.find_elements(By.CSS_SELECTOR, "table tbody tr")
    assert len(snippet_rows) == 3, \
        f"На странице должно отображаться 3 сниппета пользователя {user1.username}, найдено: {len(snippet_rows)}"

    for row in snippet_rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 7:
            author_cell = cells[6]
            author_text = author_cell.text
            assert user1.username in author_text, \
                f"Сниппет должен принадлежать пользователю {user1.username}, найден автор: {author_text}"
            assert user2.username not in author_text, \
                f"На странице не должно быть сниппетов пользователя {user2.username}, найден: {author_text}"

    for snippet in user1_snippets:
        snippet_name_element = browser.find_element(By.XPATH, f"//a[contains(text(), '{snippet.name}')]")
        assert snippet_name_element.is_displayed()

    for snippet in user2_snippets:
        try:
            snippet_name_element = browser.find_element(By.XPATH, f"//a[contains(text(), '{snippet.name}')]")
            assert False, f"Сниппет '{snippet.name}' пользователя {user2.username} не должен отображаться на странице"
        except:
            pass

    page_content = browser.find_element(By.TAG_NAME, "body").text
    assert "Общие/Публичные сниппеты" in page_content, \
        f"Текст страницы должен содержать 'Общие/Публичные сниппеты', получен: {page_content}"

# task 3

""""
1. переходим по ссылке добавления с проверкой авторизации юзера
2. Получаем доступ к полям формы
3. заполнить форму 
4. отправить форму
5. проверить добавление нового сниппета на стр
"""

@pytest.mark.django_db
def test_add_snippet_full_flow(browser, live_server):
    user = UserFactory()
    password = "defaultpassword"

    browser.get(f"{live_server.url}{reverse('MainApp:home')}")
    try:
        toggler = browser.find_element(By.CLASS_NAME, "navbar-toggler")
        if toggler.is_displayed():
            toggler.click()
            WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.ID, "navbarContent"))
            )
    except:
        pass

    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
    )
    browser.find_element(By.CSS_SELECTOR, "input[name='username']").send_keys(user.username)
    browser.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(password)
    login_form = browser.find_element(By.CSS_SELECTOR, "form[action*='custom_login']")
    browser.execute_script("arguments[0].submit();", login_form)
    WebDriverWait(browser, 10).until(
        EC.url_to_be(f"{live_server.url}{reverse('MainApp:home')}")
    )

    browser.get(f"{live_server.url}{reverse('MainApp:snippet-add')}")

    form = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "form.w-50"))
    )

    form.find_element(By.NAME, "name").send_keys("UI Selenium Test")
    form.find_element(By.NAME, "lang").send_keys("Python")
    form.find_element(By.NAME, "code").send_keys("print('Hello from Selenium!')")
    form.find_element(By.NAME, "description").send_keys("UI тестовое описание")

    public_checkbox = form.find_element(By.NAME, "public")
    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", public_checkbox)
    time.sleep(0.2)
    browser.execute_script("arguments[0].click();", public_checkbox)

    submit_btn = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
    time.sleep(0.2)
    browser.save_screenshot("before_click_submit_btn.png")
    browser.execute_script("arguments[0].click();", submit_btn)

    print("Current URL:", browser.current_url)
    print("Page source:", browser.page_source)

    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//input[@value='UI Selenium Test']"))
    )








