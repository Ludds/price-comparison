import requests
from bs4 import BeautifulSoup
import time
import smtplib
from getpass import getpass
import sys

USER = ''
PASS = ''
cheapestprice = sys.maxsize
counter = 0
loop = True
URL = 'https://www.prisjakt.nu'
searchterm = None
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
s = smtplib.SMTP('smtp-mail.outlook.com',587)
type(s)
s.ehlo()
s.starttls()

print('This script will let you search for a product and will kepp track of it and its price\nwhen it dropps in price it will send you and email\nif you dont enter a min price the program will exit after the first drop')

while USER == '' or PASS == '':
    USER = input('Enter an email: ')
    PASS = getpass()
    if USER == '' or PASS == '':
        print('These fields needs to be filled!')
    else:
        try:
            s.login(USER, PASS)
            break
        except smtplib.SMTPException:
            print('Wrong e-mail/password, try again!')
            USER = ''
            PASS = ''

while searchterm is None:
    prodcut = input('Name of product: ')
    searchpage = 'https://www.prisjakt.nu/search?search=' + prodcut
    page = requests.get(searchpage, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    for a in soup.find_all(class_='ProductLink-bvh34t-1 bcUurC', href=True):
        searchterm = a['href']
        if not(searchterm is None):
            break
    if searchterm is None:
        print('That product could not be find, please try again!')

page = requests.get(URL + searchterm, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
title = soup.find(class_="Title-sc-1i89wok-2 hligmk").get_text()

print("\nFound product: " + title)

lowestprice = input('Enter the lowest price in kr (optional):')
if not lowestprice:
    lowestprice = sys.maxsize


while loop:
    page = requests.get(URL + searchterm, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.find(class_="Title-sc-1i89wok-2 hligmk").get_text()

    prices = soup.find_all(class_="PriceLabel-sc-1uc1vg9-0 jKAqaE")

    price = sys.maxsize

    for i in prices:
            first = i.get_text().replace("\xa0", "")
            last = first.replace("kr", "")
            temp = int(last)
            
            if temp < price:
                price = temp

    counter += 1
    print("Priser jämförda: " + str(counter))
    
    if cheapestprice > price:
        cheapestprice = price
        if counter > 1 or price < int(lowestprice):
            for a in soup.find_all(class_='Link-sc-1rysriw-1 hqjkdU', href=True):
                productURL = a['href']
                if not(productURL is None): 
                    break 
            data = 'Subject: Price has dropped on ' + title + '!\n\n' + title + ' has dropped in price down to ' + str(price) + ' kr\nBuy it on ' + productURL
            s.sendmail(USER, USER, data)
            loop = False
            print("\n\nTracking was stopped product has dropped below you lowest price!")    


    if loop is True:
        print("Waiting half a day before comparing the prices again!")
        time.sleep(43200)
s.quit()