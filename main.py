from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import requests, os, zipfile, pickle
from selenium.webdriver.common.by import By
import time 



WORK_FOLDER = "work_folder"
WORDWALL_LOGIN_URL = "https://wordwall.net/account/login"
WORDWALL_CREATE_URL = "https://wordwall.net/create/entercontent?templateId=36"

def get_browser_path() -> str:
    """
        return str path to browser
    """
    BROWSER_URL = "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%2F1070094%2Fchrome-win.zip?generation=1668133267247822&alt=media"
    folder = "browser"
    folder_path = os.path.join(WORK_FOLDER, folder)
    folder_path2 = os.path.join(folder_path, "chrome-win")

    try:
        if os.path.exists(os.path.join(folder_path2, "chrome.exe")):
            return os.path.join(folder_path2, "chrome.exe")
        else:
            raise FileNotFoundError

    except (FileNotFoundError, IndexError):

        if not os.path.exists(WORK_FOLDER):
            os.mkdir(WORK_FOLDER)

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        response = requests.get(BROWSER_URL)
        browser_zip = os.path.join(folder_path, "chrome-win.zip")
        open(browser_zip, "wb").write(response.content)

        with zipfile.ZipFile(browser_zip) as zip_ref:
            zip_ref.extractall(folder_path)

        os.remove(browser_zip)
        return os.path.join(folder_path2, "chrome.exe")

def get_webdriver_path() -> str:
    """
        return str path to webdriver
    """
    webdriver_link = "https://chromedriver.storage.googleapis.com/109.0.5414.74/chromedriver_win32.zip"
    folder = "driver"
    folder_path = os.path.join(WORK_FOLDER, folder)

    try:
        return os.path.join(folder_path, os.listdir(folder_path)[0])

    except (FileNotFoundError, IndexError):
        
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        
        response = requests.get(webdriver_link)
        webdriver_zip = os.path.join(folder_path, "chromedriver_win32.zip")
        open(webdriver_zip, "wb").write(response.content)

        with zipfile.ZipFile(webdriver_zip) as zip_ref:
            zip_ref.extractall(folder_path)

        os.remove(webdriver_zip)
        return os.path.join(folder_path, "chromedriver.exe")

def prepare_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.binary_location = get_browser_path()
    options.add_argument('headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    return webdriver.Chrome(executable_path=get_webdriver_path(), chrome_options=options)

def first_enter(driver, username, password):
    driver.get(WORDWALL_LOGIN_URL)
    driver.find_element('id', "Email").send_keys(username)
    driver.find_element('id', "Password").send_keys(password)
    checkbox = driver.find_element('id', "RememberMe")
    checkbox.click()
    checkbox.send_keys(Keys.ENTER)
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.TAG_NAME,"title"))
    title = driver.find_element(By.TAG_NAME,  'title').get_attribute('text')

    if title == "My Activities":
        pickle.dump(driver.get_cookies() , open(os.path.join(WORK_FOLDER, "cookies.pkl"), "wb"))
        return True

    else:
        return False

def enter_by_cookies(driver):
    try:
        cookies = pickle.load(open(os.path.join(WORK_FOLDER, "cookies.pkl"), "rb"))
    except:
        return False
    
    driver.get(WORDWALL_LOGIN_URL)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.get(WORDWALL_CREATE_URL)

    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.TAG_NAME,"title"))
    title = driver.find_element(By.TAG_NAME,  'title').get_attribute('text')
    if title == "Wordwall | Create better lessons quicker":
        return True
    else:
        return False

def fill_form(driver, sentences: str, miss: list, incorect: list, xpath_editor, xpath_miss, xpath_incrct):
    sentense_form = driver.find_element(By.XPATH, xpath_editor)
    sentense_form.send_keys(sentences)
    sentense_form.send_keys(Keys.CONTROL + Keys.HOME)
    print("paste sentense")

    for positions in miss:
        
        sentense_form.send_keys(Keys.RIGHT * positions[0] + (Keys.SHIFT + Keys.RIGHT* positions[1]))
        time.sleep(0.2)
        # text = 'Add ' + f'"{sentence[positions[0]:sum(positions)]}"'
        # WebDriverWait(driver, 20).until(EC.text_to_be_present_in_element((By.XPATH, xpath_miss), text))
        driver.find_element(By.XPATH, xpath_miss).click()
    sentense_form.click()
    print("paste miss")

    for word in incorect:
        driver.find_element(By.XPATH, xpath_incrct).click()
        driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div[2]/input').send_keys(word)
        driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div/div[3]/button').click()
    print("paste inc")

def create_game(driver, title, quantity,  list_sentences):
    driver.get(WORDWALL_CREATE_URL)
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.CLASS_NAME, "js-activity-title"))
    #fill if only one form
    title_of_game = driver.find_element(By.CLASS_NAME, "js-activity-title")
    title_of_game.send_keys(Keys.CONTROL + "a")
    title_of_game.send_keys(Keys.DELETE)
    title_of_game.send_keys(title)

    xpath_editor = '//*[@id="editor_component_0"]/div/div/div/div[3]/div[1]'
    xpath_miss = '//*[@id="editor_component_0"]/div/div/div/div[3]/div[2]/a/span[2]'
    xpath_incrct = '//*[@id="editor_component_0"]/div/div/div/div[3]/div[3]/a'
    

    fill_form(driver, list_sentences[0].get('sentences'), list_sentences[0].get('miss'), list_sentences[0].get('incorect'), xpath_editor, xpath_miss, xpath_incrct)

    #fill other forms
    if quantity > 1:
        xpath_editor_more = '//*[@id="editor_div"]/div[{}]/div[3]/div[1]'#start from 3
        xpath_miss_more = '//*[@id="editor_div"]/div[{}]/div[3]/div[2]/a/span[2]'
        xpath_incrct_more = '//*[@id="editor_div"]/div[{}]/div[3]/div[3]/a'

        for indx, catalog in enumerate(list_sentences[1:]):
            curr = indx + 3
            driver.find_element(By.XPATH, f'//*[@id="editor_div"]/div[{curr}]').click()
            fill_form(driver, catalog.get('sentences'), catalog.get('miss'), catalog.get('incorect'), xpath_editor_more.format(curr), xpath_miss_more.format(curr), xpath_incrct_more.format(curr))
    
    driver.find_element(By.XPATH, '//*[@id="outer_wrapper"]/div[2]/div[7]/button').click()
    print('create, name = ', title)


def get_sentences(driver, phrase):
    sentences_out = []
    base_url = 'https://sentencedict.com/{}_{}.html'
    phrase = phrase.strip().replace(' ', '%20')
    url = base_url.format(phrase, 1)
    driver.get(url)

    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.TAG_NAME,"title"))
    title = driver.find_element(By.TAG_NAME,  'title').get_attribute('text')
    if title == "Sentence dictionary online - Good sentence examples for every word!":
        return False

    total = driver.find_element(By.XPATH, '/html/head/meta[2]').get_attribute('content')
    pre_total = total[:total.find(' ')]
    total = sum([int(i) for i in pre_total.split("+")])
    
    sentences = driver.find_elements(By.XPATH, '//*[@id="all"]')[0].text
    sentences = sentences.split('\n')
    for val in sentences:
        sentences_out.append(val[val.find(' ')+1:])

    if total <= 30:
        return {
        'total' : total,
        'sentences' : sentences_out    
        }

    url = base_url.format(phrase, 2)
    driver.get(url)

    sentences = driver.find_elements(By.XPATH, '//*[@id="all"]')[0].text
    sentences = sentences.split('\n')
    for val in sentences:
        sentences_out.append(val[val.find(' ')+1:])

    return {
        'total' : len(sentences_out),
        'sentences' : sentences_out    
        }
    



    
    


if __name__=="__main__":

    driver = prepare_driver()
    # first_enter(driver, 'gar111@gmail.com', '040399')
    print(f"enter by cookues = {enter_by_cookies(driver)}")
    # driver.get(WORDWALL_CREATE_URL)
    b = [
            {
                'sentences' : "1. Our bus won't start because the battery is flat.\n2. We had to sprint to catch the bus.\n",
                'miss' : [
                    (43, 4), #flat
                    (35, 7), #battery
                    (23, 7), #'because'
                    (3, 7), #'Our bus'
                    (75, 5)
                ],
                'incorect' : [
                    "rrrr",
                    "ddddd"
                ]
            },
            {
                'sentences' : "1. Our bus won't start because the battery is flat.\n2. We had to sprint to catch the bus.\n",
                'miss' : [
                    (43, 4), #flat
                    (35, 7), #battery
                    (23, 7), #'because'
                    (3, 7), #'Our bus'
                    (75, 5)
                ],
                'incorect' : [
                    "rrrr",
                    "ddddd"
                ]
            },
        ]
    create_game(driver, "gay", len(b), b)
    
    
    WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.TAG_NAME,"fewawda"))

    # print(get_sentences(driver, 'Added'))