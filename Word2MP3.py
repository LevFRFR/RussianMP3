# Initiate browser, query word, get network flow with specific name, get its GET Request URL, download the file with the words name in it.


# load in required packages
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import requests
import sys
import os


# writes all the logs into a 'network_log.json' file.
def writeLogsAsJSON(logs):
    # Opens a writable JSON file and writes the logs in it
    with open("network_log.json", "w", encoding="utf-8") as f:
        f.write("[")

        # Iterates every logs and parses it using JSON
        for log in logs:
            network_log = json.loads(log["message"])["message"]

            # Checks if the current 'method' key has any
            # Network related value.
            if("Network.response" in network_log["method"]
                    or "Network.request" in network_log["method"]
                    or "Network.webSocket" in network_log["method"]):

                # Writes the network log to a JSON file by
                # converting the dictionary to a JSON string
                # using json.dumps().
                f.write(json.dumps(network_log)+",")
        f.write("{}]")

        return None


# read the JSON File and parse it using
def parseLogsJSON():
    # json.loads() to find the urls containing images.
    json_file_path = "network_log.json"
    
    with open(json_file_path, "r", encoding="utf-8") as f:
        logs = json.loads(f.read())
    
    os.remove(json_file_path)

    return logs


# searches the logs for the specific link
def getVoiceLink(logs):
    # Iterate the logs
    for log in logs:

        # Except block will be accessed if any of the
        # following keys are missing.
        try:
            # URL is present inside the following keys
            url = log["params"]["request"]["url"]

            if 'voice' in url:
                return url

        except Exception as e:
            pass


# download file as .mp3
def downloadMP3(link, userAgent):
    headers = {'User-Agent':userAgent}

    response = requests.get(link, headers=headers)

    with open(word + '.mp3', 'wb') as f:
        f.write(response.content)

    return None


def startDriver():
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--mute-audio')
    options.add_argument('log-level=3') # suppress all warnings except fatal errors
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # suppress DevTools info

    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), desired_capabilities=capabilities, options=options)


def getRussianWordPronounciation(word = 'нормально'):

    print("Setting Selenium WebDriver Options & Capabilities")
    driver = startDriver()

    mainURL = 'https://context.reverso.net/translation/russian-english/' + word
    driver.get(mainURL)

    driver.find_element(By.XPATH, '//*[@id="search-links"]/button[1]').click()

    # Gets all the logs from performance in Chrome
    logs = driver.get_log("performance")

    print("Gathering Network Logs")
    writeLogsAsJSON(logs)

    print("Getting User-Agent")
    userAgent = driver.execute_script("return navigator.userAgent")

    print("Quitting Selenium WebDriver")
    driver.quit()

    print("Parsing Logs")
    logs = parseLogsJSON()

    print("Getting the Link")
    link = getVoiceLink(logs)

    print("Downloading MP3 File")
    downloadMP3(link, userAgent)

    if os.path.exists( word + '.mp3' ):
        print(f'"{word}.mp3" is Ready to Listen\n')

    return None


if __name__ == '__main__':

    words = sys.argv[1:]

    for word in words:
        getRussianWordPronounciation( word )