from selenium import webdriver
from time import sleep
from config import username, password, discord_token, discord_channel_id
from pickles import load_pickle, store_pickle

import discord


def main():
    if check_online():
        return

    driver = get_page_driver()

    # Load the page
    driver.get("https://sisastudent.uantwerpen.be")
    wait_for_load(driver)
    assert "Universiteit Antwerpen" in driver.title

    sisa_login(driver)

    # Navigate to cijfers
    click_by_id(driver, "win0divPTNUI_LAND_REC_GROUPLET$4")
    click_by_id(driver, "TERM_GRID$0_row_0")  # row 0 is the current year

    # Check of er een cijfer staat
    # $0 is the first course in your results list
    # make sure this is a course of which you're waiting for the results
    result = driver.find_element_by_id("STDNT_ENRL_SSV1_CRSE_GRADE_OFF$1").text

    if result != ' ':
        print("Punten staan online")
        make_announcement("Punten staan online (volgens mijn sisa bot toch)")
        set_online()
    else:
        print("Nog niet online")
        make_announcement("Punten staan nog niet online(volgens mijn sisa bot toch)")

    driver.close()


def check_online():
    # Checks whether this script has already detected that the results are online
    return load_pickle("online.pickle", False)


def set_online():
    store_pickle("online.pickle", True)


def get_page_driver():
    # Selenium configuration
    opts = webdriver.FirefoxOptions()
    opts.headless = False
    driver = webdriver.Firefox(options=opts)
    return driver


def wait_for_load(driver):
    sleep(3)


def sisa_login(driver):
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
        channel = client.get_channel(discord_channel_id)
        await channel.send(message)
        await client.close()

    client.run(discord_token)


if __name__ == '__main__':
    main()
