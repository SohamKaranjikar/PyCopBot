#!/usr/bin/env python3
import requests
import bs4 as bs
from splinter import Browser
from splinter import request_handler
import helpers
import time
import config


class supremeBot(object):
    path = ""
    linksToAvoid = []
    
    def __init__(self, **info):
        self.base_url = 'http://www.supremenewyork.com/'
        self.shop = 'shop/all/'
        self.checkout = 'checkout/'
        self.info = info

    def initializeBrowser(self):
        global path
        driver = self.info["driver"]
        path = helpers.get_driver_path(driver)
        if driver == "geckodriver":
            self.b = Browser()
        elif driver == "chromedriver":
            executable_path = {"executable_path": path}
            self.b = Browser('chrome',headless = False ,**executable_path)


    def findProduct(self):
        try:
            r = requests.get(
                "{}{}{}".format(
                    self.base_url,
                    self.shop,
                    self.info['category'])).text
            soup = bs.BeautifulSoup(r, 'lxml')

            temp_tuple = []
            temp_link = []
            
            for link in soup.find_all('a', href=True):
                temp_tuple.append((link['href'], link.text))
            #print(temp_tuple)
            for i in temp_tuple:
                if (any(x in i[1] for x in self.info['product'])
                    and (i[0] in self.linksToAvoid) != True):
                    r = requests.get(
                        "{}{}".format(
                        self.base_url, str(i[0]))).text
                    soup = bs.BeautifulSoup(r, 'html.parser')
                    if("<b class=\"button sold-out\">sold out</b>"  in str(soup.find_all('b'))):
                        self.linksToAvoid.append(i[0])
                        print("Sold out: "+str(i[1]))
                    else:
                        temp_link.append(i[0])
                if(len(temp_link)!=0 and (i[1] == self.info['color'])
                   and (i[0] in self.linksToAvoid) != True):
                    temp_link.append(i[0])
                    break
                elif(len(temp_link)!=0 and ("" == self.info['color'])
                     and (i[0] in self.linksToAvoid) != True):
                    temp_link.append(i[0])
                    break
                    

            self.final_link = temp_link[len(temp_link)-1]
            return True
        except:
            return False

    def addToCart(self):
        self.b.visit(
            "{}{}".format(
                self.base_url, str(
                    self.final_link)))
        if(self.info['size'] == ""):
            #do nothing
            None
        else:
            self.b.find_option_by_text(self.info['size']).click()
            
        try:
            self.b.find_by_value('add to cart').click()
            try:
                time.sleep(.1)
                self.checkoutFunc()
            except:
                time.sleep(1)
                self.addToCart()
            else:
                print("Failed adding to cart")
        except:
            print("OOS, Checking diff color")
            self.info['color']=""
            self.linksToAvoid.append(self.final_link)
            self.findProduct()
            self.addToCart()

    def checkoutFunc(self):
        self.b.visit("{}{}".format(self.base_url, self.checkout))

        self.b.fill("order[billing_name]", self.info['namefield'])
        self.b.fill("order[email]", self.info['emailfield'])
        self.b.fill("order[tel]", self.info['phonefield'])

        self.b.fill("order[billing_address]", self.info['addressfield'])
        self.b.fill("order[billing_city]", self.info['city'])
        self.b.fill("order[billing_zip]", self.info['zip'])
        self.b.select("order[billing_country]", self.info['country'])

        self.b.fill("riearmxa", self.info['number'])
        self.b.select("credit_card[month]", self.info['month'])
        self.b.select("credit_card[year]", self.info['year'])
        self.b.fill("credit_card[meknk]", self.info['ccv'])
        
        self.b.find_by_css('.terms').click()
        
        self.b.find_by_value("process payment").click()
    
    def quitBot(self):
        self.b.quit()


if __name__ == "__main__":
    
    BOT = supremeBot(**config.INFO)
    # Flag to set to true if you want to reload the page continously close to drop.
    found_product = False
    max_iter = 20
    counter = 1
    while not found_product:
        found_product = BOT.findProduct()
        print("Tried ", counter, " times")
        counter += 1
        time.sleep(.892)
        BOT.linksToAvoid = []
    if not found_product:
        raise Exception("Couldn't find product. Sry bruh")
    BOT.initializeBrowser()
    BOT.addToCart()
