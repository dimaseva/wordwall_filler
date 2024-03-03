from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import requests, os, zipfile, pickle
from selenium.webdriver.common.by import By
import time 
import requests
import bs4 as bs



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

    if title in ["My Activities", "Мої вправи", "Мои занятия"]:
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
    if "Wordwall | " in title:
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
        xpath_editor_more = '//*[@id="editor_component_0"]/div/div/div[{}]/div[3]/div[1]'  # start from 2
        xpath_miss_more = '//*[@id="editor_component_0"]/div/div/div[{}]/div[3]/div[2]/a/span[2]'
        xpath_incrct_more = '//*[@id="editor_component_0"]/div/div/div[{}]/div[3]/div[3]/a'

        for indx, catalog in enumerate(list_sentences[1:]):
            curr = indx + 2
            driver.find_element(By.XPATH, f'//*[@id="editor_div"]/div[{curr}]').click()
            fill_form(driver, catalog.get('sentences'), catalog.get('miss'), catalog.get('incorect'), xpath_editor_more.format(curr), xpath_miss_more.format(curr), xpath_incrct_more.format(curr))
    
    WebDriverWait(driver, timeout=10).until(lambda d: d.find_element(By.XPATH, '//*[@id="outer_wrapper"]/div[2]/div[7]/button'))
    time.sleep(0.2)
    driver.find_element(By.XPATH, '//*[@id="outer_wrapper"]/div[2]/div[7]/button').click()
    print('create, name = ', title)


def get_sentences(phrase):
    sentences_out = []
    
    url = 'https://sentencedict.com/wordQueryDo.php'

    headers = {
        'authority': 'sentencedict.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
        'cache-control': 'max-age=0',
        'origin': 'https://sentencedict.com',
        'referer': 'https://sentencedict.com/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    data = {
        'q': '',
        'word': phrase,
        'directGo': '1',
    }

    response = requests.post(url=url, headers=headers, data=data)
    content = response.content

    soup = bs.BeautifulSoup(content,'html.parser')

    elem_all = soup.find("div", {'id' : 'all'})

    if elem_all:
        for val in elem_all:
            check = str(val.text)
            if check and check != '\n':
                sentences_out.append(check[check.find(' ')+1:])
        
        return sentences_out

    elem_content = soup.find("div", {'id' : 'content'})
    for val in elem_content:
        check = str(val.text)
        if check and check != '\n':
            sentences_out.append(check[check.find(' ')+1:check.rfind('.')+1])
    return sentences_out



    

if __name__=="__main__":

    # driver = prepare_driver()
    # first_enter(driver, 'gar111@gmail.com', '040399')
    # print(f"enter by cookues = {enter_by_cookies(driver)}")
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
    # create_game(driver, "gay", len(b), b)
    # get_sentences('I consider myself')
    # get_sentences('sajhflw')
    # get_sentences('bus')
    
    # WebDriverWait(driver, timeout=60).until(lambda d: d.find_element(By.TAG_NAME,"fewawda"))

    # print(get_sentences(driver, 'Added'))