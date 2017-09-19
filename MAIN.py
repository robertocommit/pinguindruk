from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

proxyIP = "127.0.0.1"
proxyPort = 9150
proxy_settings = {
  "network.proxy.type": 1,
  "network.proxy.socks": proxyIP,
  "network.proxy.socks_port": proxyPort,
  "network.proxy.socks_remote_dns": True,
}

firefox_profile = FirefoxProfile()
for key, value in proxy_settings.items():
    firefox_profile.set_preference(key, value)
capa = DesiredCapabilities.FIREFOX
capa["pageLoadStrategy"] = "none"


def main():
  browser = webdriver.Firefox(firefox_profile, capabilities=capa, executable_path='/home/robimalco/Like_Desktop/drivelog/geckodriver')
  browser.get('https://pinguindruck.de/shop/postkarten')
  browser.find_elements_by_xpath('//*[@id="easy_modus"]/div[1]')[0].click()
  browser.find_elements_by_xpath('//*[@id="format_select_title"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="format_select_msa_3"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="paper_select_title"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="paper_select_msa_1"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="color_select_title"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="color_select_msa_1"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="charge_select_title"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="charge_select_msa_1"]')[0].click()
  browser.find_elements_by_xpath('//*[@id="new_price"]')[0].click()


if __name__ == '__main__':
    main()
