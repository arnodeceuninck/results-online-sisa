from selenium import webdriver, common
from time import sleep
from config import username, password, discord_token, discord_channel_ids, semesters_to_check
from pickles import load_pickle, store_pickle

from datetime import datetime

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import discord

last_message = "Checking results on Sisa (this might take a while)..."


def main(manually=True, test=False):
    # Als ze al eerder allemaal gedetecteerd zijn, moeten we niet nog eens checken (tenzij handmatig opgeroepen)
    if not manually and check_online():
        return

    year = 0 if not test else 1  # 0 is current year, 1 previous year
    driver = get_results_page(year)

    num_courses, results = check_all_courses(driver, semesters_to_check=semesters_to_check)

    num_results = len(results)

    announcement = f"Momenteel hebben we punten voor {num_results} van de {num_courses} vakken uit semester {semesters_to_check}:\n"
    for course in results:
        announcement += f"- {course.description}\n"
    if test:
        announcement += "Note: Dit is een test en gaat over de resultaten van vorig jaar. \n"
    if manually:
        announcement += f"Laatste succesvolle automatische test was om {get_logged_time()}.\n"

    # Kijk of er een punt is bijgekomen, en if so, post it
    last_results = load_pickle("num_results.pickle", 0)
    # Niet posten bij manuele oproepen om dubbele posts te vermijden
    if not manually and num_results > last_results:
        # Er zijn punten bijgekomen
        make_announcement(announcement)
        store_pickle("num_results.pickle", num_results)

    if not manually:
        log_time()

    print(announcement)
    driver.close()

    return announcement


def get_average():
    total_sp = 0
    total_sum = 0
    for i in range(3):  # TODO: Zelf bepalen hoeveel jaren er zijn
        print(f"Checking year {i}")
        driver = get_results_page(i)
        num_courses, courses = check_all_courses(driver)
        for course in courses:
            if not isinstance(course.result, float):
                print(f"Skipping {course.description} with result {course.result}")
                continue
            total_sum += course.sp * course.result
            total_sp += course.sp
    avg = total_sum / total_sp
    return avg


def get_results_page(year_id):
    driver = get_page_driver()
    load_page(driver)
    sisa_login(driver)
    update_status("Navigating to results...")
    click_by_id(driver, "win0divPTNUI_LAND_REC_GROUPLET$4")
    update_status("Selecting year...")
    click_by_id(driver, f"TERM_GRID$0_row_{year_id}")
    return driver


def update_status(msg):
    print(msg)
    global last_message
    last_message = msg


def get_last_message():
    return last_message


def get_onderscheiding(avg):
    avg *= 5  # omzetten van op 20 naar op 100
    assert avg <= 100
    if avg < 50:
        return "Onvoldoende"
    elif avg < 68:
        return "Voldoende"
    elif avg < 77:
        return "Onderscheiding"
    elif avg < 85:
        return "Grote onderscheiding"
    else:
        return "Grootste onderscheiding"


class Course:
    def __init__(self, description, sp, semester, result):
        self.description = description
        self.sp = float(sp.replace(',', '.'))
        self.semester = semester
        # print(description)
        try:
            self.result = float(result.replace(',', '.'))
        except ValueError:
            self.result = result


def check_all_courses(driver, semesters_to_check=None, with_results_only=True):
    if semesters_to_check is None:
        semesters_to_check = ["S01", "S02", "S12"]

    update_status(f"Checking courses of semester {semesters_to_check}...")

    results = []

    current_course_id = 0
    num_courses = 0  # number of courses in the given semester (with or without result)
    while True:
        try:
            course = get_course_info(current_course_id, driver)
            current_course_id += 1

            if course.semester not in semesters_to_check:
                continue

            if with_results_only and (course.result is not None and course.result != '' and course.result != ' '):
                results.append(course)

            num_courses += 1
        except common.exceptions.NoSuchElementException:
            break

    return num_courses, results


def get_course_info(course_id, driver):
    result = driver.find_element_by_id(f"STDNT_ENRL_SSV1_CRSE_GRADE_OFF${course_id}").text
    course = driver.find_element_by_id(f"CLASS_TBL_VW_DESCR${course_id}").text
    sp = driver.find_element_by_id(f"STDNT_ENRL_SSV1_UNT_TAKEN${course_id}").text
    semester = driver.find_element_by_id(f"STDNT_ENRL_SSV1_SESSION_CODE${course_id}").text
    return Course(description=course, sp=sp, semester=semester, result=result)


def load_page(driver):
    attempt = 0
    while attempt < 3:
        try:
            update_status("Loading page...")
            driver.get("https://sisastudent.uantwerpen.be")
            wait_for_load(driver)
            assert "Universiteit Antwerpen" in driver.title
            return
        except AssertionError:
            attempt += 1


def check_online():
    # Checks whether this script has already detected that the results are online
    return load_pickle("online.pickle", False)


def set_online():
    store_pickle("online.pickle", True)


def get_page_driver():
    # Selenium configuration
    opts = webdriver.FirefoxOptions()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    return driver


def wait_for_load(driver):
    # Still not perfect, if this doesn't work on your system, increase seconds_ready

    sleep_time = 0.01
    max_wait = 20
    seconds_ready = 2  # Minimum page must be ready before considered completely loaded

    total_ready = 0
    total_sleep = 0

    while total_ready < seconds_ready:
        if total_sleep > max_wait:
            raise Exception
        if driver.execute_script("return document.readyState") == "complete":
            total_ready += sleep_time
            # print(f"ready {total_ready}")
        else:
            total_ready = 0
            # print("Not ready")
        sleep(sleep_time)
        total_sleep += sleep_time
    # print("Loaded")


def sisa_login(driver):
    update_status("Logging in...")
    enter_text("username", username, driver)
    enter_text("password", password, driver)
    driver.find_element_by_name("_eventId_proceed").click()
    wait_for_load(driver)


def enter_text(field_id, text, driver):
    element = driver.find_element_by_id(field_id)
    element.clear()
    element.send_keys(text)


def click_by_id(driver, id):
    driver.find_element_by_id(id).click()
    wait_for_load(driver)


def make_announcement(message):
    client = discord.Client()

    @client.event
    async def on_ready():
        for discord_channel_id in discord_channel_ids:
            channel = client.get_channel(discord_channel_id)
            await channel.send(message)
        await client.close()

    client.run(discord_token)


def log_time():
    store_pickle("last.pickle", datetime.now())


def get_logged_time():
    return load_pickle("last.pickle", "unknown")


if __name__ == '__main__':
    while True:
        try:
            main(manually=False, test=False)
        except:
            print(f"An error occured at {datetime.now()}")
        sleep(30)
