"""
Page Object Model for PyTodo Pro (Chapter 6: keep test logic apart from UI
locators, so a changed button only needs fixing in one place).
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE = "http://127.0.0.1:5000"


class BasePage:
    def __init__(self, driver):
        self.d = driver
        self.wait = WebDriverWait(driver, 5)

    def open(self, path):
        self.d.get(BASE + path)
        return self

    def heading(self):
        return self.d.find_element(By.TAG_NAME, "h1").text

    def error(self):
        found = self.d.find_elements(By.CSS_SELECTOR, "p.error")
        return found[0].text if found else None

    def shot(self, path):
        self.d.save_screenshot(path)


class AuthPage(BasePage):
    def submit(self, username, password):
        self.d.find_element(By.NAME, "username").send_keys(username)
        self.d.find_element(By.NAME, "password").send_keys(password)
        old = self.d.find_element(By.TAG_NAME, "html")
        self.d.find_element(By.CSS_SELECTOR, "form button[type=submit]").click()
        self.wait.until(EC.staleness_of(old))          # wait for the next page to load
        return TaskListPage(self.d)


class RegisterPage(AuthPage):
    def open(self):
        return super().open("/register")


class LoginPage(AuthPage):
    def open(self):
        return super().open("/login")


class TaskListPage(BasePage):
    def open(self, query=""):
        return super().open("/" + query)

    def new_task(self, title, category=None, due_iso=None):
        old = self.d.find_element(By.TAG_NAME, "html")
        self.d.find_element(By.LINK_TEXT, "+ New Task").click()
        self.wait.until(EC.staleness_of(old))
        form = TaskFormPage(self.d)
        form.fill(title, category, due_iso)
        form.save()
        return self

    def rows(self):
        return self.d.find_elements(By.CSS_SELECTOR, "table.task-table tbody tr")

    def row(self, title):
        for r in self.rows():
            if title in r.text:
                return r
        return None

    def badge(self, title):
        r = self.row(title)
        return r.find_element(By.CSS_SELECTOR, ".badge").text if r else None

    def toggle(self, title):
        old = self.d.find_element(By.TAG_NAME, "html")
        self.row(title).find_element(By.CSS_SELECTOR, "button.check-btn").click()
        self.wait.until(EC.staleness_of(old))

    def delete(self, title):
        old = self.d.find_element(By.TAG_NAME, "html")
        self.row(title).find_element(By.CSS_SELECTOR, "button.link-btn").click()
        self.wait.until(EC.alert_is_present()).accept()
        self.wait.until(EC.staleness_of(old))

    def filter_category(self, name):
        old = self.d.find_element(By.TAG_NAME, "html")
        Select(self.d.find_element(By.NAME, "category")).select_by_visible_text(name)
        self.wait.until(EC.staleness_of(old))          # onchange submits the filter form

    def logout(self):
        old = self.d.find_element(By.TAG_NAME, "html")
        self.d.find_element(By.LINK_TEXT, "Log out").click()
        self.wait.until(EC.staleness_of(old))
        return LoginPage(self.d)


class TaskFormPage(BasePage):
    def fill(self, title, category=None, due_iso=None):
        t = self.d.find_element(By.NAME, "title")
        t.clear()
        t.send_keys(title)
        if category:
            Select(self.d.find_element(By.NAME, "category_id")).select_by_visible_text(category)
        if due_iso:
            # set the <input type=date> value directly (typing format differs per locale)
            el = self.d.find_element(By.NAME, "due_date")
            self.d.execute_script("arguments[0].value = arguments[1];", el, due_iso)

    def save(self):
        old = self.d.find_element(By.TAG_NAME, "html")
        self.d.find_element(By.CSS_SELECTOR, "form.task-form button[type=submit]").click()
        try:
            self.wait.until(EC.staleness_of(old))
        except Exception:
            pass  # browser validation blocked the submit (page did not change)


class DashboardPage(BasePage):
    def open(self):
        return super().open("/dashboard")

    def stats(self):
        out = {}
        for card in self.d.find_elements(By.CSS_SELECTOR, ".stat-card"):
            out[card.find_element(By.CSS_SELECTOR, ".stat-label").text] = \
                int(card.find_element(By.CSS_SELECTOR, ".stat-value").text)
        return out
