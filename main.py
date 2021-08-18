from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import telegram


class SigmaUSD:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("disable-infobars")
        self.chrome_options.add_argument("disable-web-security")
        self.chrome_driver_location = "chromedriver.exe"
        self.driver = webdriver.Chrome(executable_path=self.chrome_driver_location, options=self.chrome_options)
        self.driver.delete_all_cookies()
        self.bot = None

    def get_telegram_chat_id(self,title):
        chatid = 0
        updates = self.bot.get_updates()
        for update in updates:
            try:
                if update['message']['chat']['type'] == 'group':
                    if update['message']['chat']['title'] == title:
                        chatid = int(update['message']['chat']['id'])
                        break
            except:
                pass
        return chatid

    def get_data(self):
        try:
            self.driver.get('https://sigmausd.io/#/')
            time.sleep(10)
            section = self.driver.find_element_by_xpath('//section[@class="coins-info"]').find_elements_by_xpath(
                '//div[@class="coin-info tiles"]')[1]
            return int(str(
                section.find_element_by_class_name('coin-prop-footer').find_elements_by_class_name('coin-prop-right')[
                    1].find_element_by_class_name('coin-prop-right__value').text).replace('%', ''))
        except Exception as e:
            print("Exception Occured while getting Data: " + str(e))

    def check(self):
        while True:
            try:
                with open('data.json', 'r') as f:
                    data = json.load(f)
                    self.bot = telegram.Bot(token=data['token'])
                    current_ratio = self.get_data()
                    if data['ratio'] >= current_ratio:
                        self.bot.send_message(text=data['message'] + str(current_ratio),
                                              chat_id=self.get_telegram_chat_id(title=data["groupName"]))
                    # value can be changed in data.json.(data[time] is 1 it waits for 1min)
                    time.sleep(data['time'] * 60)
            except Exception as e:
                print("Exception Occured while sending Message: " + str(e))
                self.check()

    def close(self):
        self.driver.close()
        self.driver.quit()


if __name__ == '__main__':
    obj = SigmaUSD()
    obj.check()
    obj.close()
