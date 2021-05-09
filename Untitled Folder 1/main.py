from bs4 import BeautifulSoup as bs
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
import os.path
from os import path
import requests
import pandas as pd


class Test:
    def __init__(self):
        # all the fixed values
        self.URL = 'https://coinmarketcap.com/coins/'
        self.MAX = 50
        self.firefox_path = 'C:\\Users\\satvi\\Desktop\\Untitled Folder 1\\'
        self.coins_path = 'C:\\Users\\satvi\\Desktop\\Untitled Folder 1\\'
        self.coins_data_path = 'C:\\Users\\satvi\\Desktop\\Untitled Folder 1\\'


    def get_coins(self):
        name = []   #stores the name of the company
        symbol = []  #stores the symbol of the company
        link = []  #stores the symbol of the URL

        content = requests.get(self.URL, timeout=None)
        pge = bs(content.content, 'html.parser')
        
        # selecting tbody for easier selection of data
        y = pge.find('tbody')
        
        for i in y.find_all('a', class_='cmc-link'):
            
            #data is transformed into usable list
            if not i.text.startswith('$') and len(i.text)!=0:
                if i.find(class_='coin-item-symbol') == None:
                    temp = i.find(class_="crypto-symbol").text
                    if i.text.endswith(temp):
                        res = i.text[:-(len(temp))]

                else:
                    temp = i.find(class_='coin-item-symbol').text
                    if re.sub('[0-9]', '', i.text).endswith(temp):
                        res = re.sub('[0-9]', '', i.text)[:-(len(temp))]

                name.append(res)
                symbol.append(temp)
                link.append('https://coinmarketcap.com' + i['href'])
                
        #file is stored into coins.csv
        file = pd.DataFrame({'SNo':[i for i in range(1,self.MAX+1)],
                             'Name':name[:self.MAX],
                             'Symbol':symbol[:self.MAX],
                             'URL':link[:self.MAX]
                            })
        file.to_csv(os.path.join(self.coins_path ,'coins.csv'), index=False)


    def get_coin_data(self, coin_symbol):
        
        #get data from coins.csv
        p = pd.read_csv(os.path.join(self.coins_path ,'coins.csv'),index_col=0)
        url_link = p.loc[p['Symbol'] == coin_symbol]['URL'].values[0]
        res = dict()
        
        #opening firefox webdriver
        options = Options()
        options.add_argument('--headless')
        browser = webdriver.Firefox(executable_path= self.firefox_path + 'geckodriver.exe',options=options)
        browser.get(url_link)
        soup = bs(browser.page_source, 'html.parser')


        res['Symbol'] = soup.find(class_="nameSymbol___1arQV").text #symbol

        res['Name'] = soup.find(class_="sc-1q9q90x-0 iYFMbU h1___3QSYG").text[:-len(res['Symbol'])] #name

        temp_list = ['What Makes ' + res['Name'] +' Unique?',
             'Who Are the Founders of '+ res['Name'] + '?',
             'What Is '+ res['Name'] + ' (' + res['Symbol'] + ')?',
            ]

        res['Watchlist'] = soup.find_all(class_="namePill___3p_Ii")[2].text[2:-10].rstrip().strip() #watchlist

        res['Circulating Supply'] = soup.find(class_="supplyBlockPercentage___1g1SF").text #circulating supply


        #getting the url
        if soup.find(class_="buttonName___3G9lW").text.lower() == 'website':
            hover = ActionChains(browser).move_to_element(browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[1]/div[2]/div[5]/div[1]/ul/li[1]/button/div'))
            hover.perform()
            res['Url'] = browser.find_elements_by_class_name('dropdownItem___NSKhL')[0].get_attribute('href') #link
        else:
            res['Url'] = 'www.' + soup.find(class_="buttonName___3G9lW").text  #link

        # closing cookie banner
        if browser.find_element_by_class_name("cmc-cookie-policy-banner__close"):
            browser.find_element_by_class_name("cmc-cookie-policy-banner__close").click()


        # show more click
        if browser.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/button").text.lower() == 'show more':
            browser.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/button").click()

        res['Price'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[1]/td').text  #price

        res['Volume'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[5]/td').text  #volume/market cap

        res['Market Dominance'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[6]/td/span').text #market dominance

        res['Rank'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[1]/table/tbody/tr[7]/td').text  #rank

        res['Market Cap'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[2]/table/tbody/tr[1]/td/span').text  #market cap

        res['ATH DATE'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[3]/div[2]/table/tbody/tr[5]/th/small').text.partition('(')[0].rstrip()  #all time high date

        res['ATH PRICE'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[3]/div[2]/table/tbody/tr[5]/td/span').text #all time high 

        res['ATL DATE'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[3]/div[2]/table/tbody/tr[6]/th/small').text.partition('(')[0].rstrip() #all time low date

        res['ATL PRICE'] = browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div/div[3]/div/div[1]/div[2]/div[2]/div/div[3]/div[2]/table/tbody/tr[6]/td/span').text #all time low



        res[temp_list[2]] = soup.find(class_="sc-1lt0cju-0 srvSa").text.split('Related Pages')[0].split(temp_list[0])[0].split(temp_list[1])[0].split(temp_list[2])[-1]  # What is <Coin Name>?

        res[temp_list[1]] = soup.find(class_="sc-1lt0cju-0 srvSa").text.split('Related Pages')[0].split(temp_list[0])[0].split(temp_list[1])[-1]  #Who are the founders?

        res[temp_list[0]] = soup.find(class_="sc-1lt0cju-0 srvSa").text.split('Related Pages')[0].split(temp_list[0])[-1]  #What makes it unique?

        # data appended to the csv file <coins_data.csv>
        file = pd.DataFrame([res])
        if not path.exists(os.path.join(self.coins_data_path ,"coins_data.csv")):
            file.to_csv(os.path.join(self.coins_data_path ,"coins_data.csv"), header=True, index=False)
        else:
            file.to_csv(os.path.join(self.coins_data_path ,"coins_data.csv"), mode='a', header=False, index=False)

        browser.quit()

if __name__ == "__main__":
    t = Test()
    t.get_coins()
    t.get_coin_data('BTC')
