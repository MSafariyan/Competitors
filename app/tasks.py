from bs4 import BeautifulSoup
import lxml.html
import re
import requests
from requests_html import HTMLSession
import pandas as pd
import time
import os.path
import mysql.connector
import csv



mydb = mysql.connector.connect(host='localhost', user='mahdi', password='',database='simplecrawl')

cursor = mydb.cursor()


def make_table_clean():
    try:
        print("============Cleaning Table============")
        query = "TRUNCATE TABLE simplecrawl.books"
        cursor.execute(query)
        print("Status: Cleaning was successful")
    except Exception as e:
        print("==Cleaning database has been failed.==")
        print(f"Error Exectopn: {e}")

def fill_table():
    try:
        print("==========Updating Database===========")
        if os.path.isfile('data/zabanshop.csv') == True:
            rows = csv.reader(open('data/zabanshop.csv'))
            for row in rows:
                cursor.execute('INSERT INTO books (name,price,oldprice,specialprice,img) VALUES(%s,%s,%s,%s,%s)', row)
            cursor.execute("DELETE FROM `simplecrawl`.`books` WHERE (`id` = '1')")
        print("Status: Updating was succesful")
    except Exception as e:
        print("Status: Updating failed")
        print(f"Error exception: {e}")

def create_csv(records):
    try:
        print("=============Creating CSV=============")
        if os.path.isdir('data') == False:
            os.mkdir('data')
        if os.path.isfile('data/zabanshop.csv') == True:
            os.remove("data/zabanshop.csv")
        df = pd.DataFrame(records, columns=['name','price','oldprice','specialprice', 'img'])
        df.to_csv('data/zabanshop.csv', index=False, encoding='utf-8')
        print("CSV file is ready")
    except Exception as e:
        print("Status: Creating failed")
        print(f"Error Exception: {e}")


def zabanshop():
    try:
        print("============Try to connect============")
        http_proxy  = "127.0.0.1:9150"
        proxy = {'http': http_proxy}
        html = requests.get('https://zaban.shop/')
        print("fetching: zabanshop")
        root = lxml.html.fromstring(html.text)
        hrefs = root.xpath("//li[contains(@class, 'has-sub-category')]/ul/li/a")
        records = []
        count = 1
        len_hrefs = len(hrefs)
        print("Links = ",len_hrefs)
        for href in hrefs:
            url = href.attrib['href'] + '/?pageitems=120' + '&only_available=1'
            if re.search('\d*_\d*_\d*', url):
                print(f"[{count}/" + str(len_hrefs) + "]")
                response = requests.get(url, proxies=proxy).text
                time.sleep(1)
                soup = BeautifulSoup(response, 'html.parser')
                items = soup.find_all('div', attrs={'class':'product-item'})
                for item in items:
                    if item.find("a", attrs={'class':'product-name'}) == None:
                        pass
                    elif item.find('span', {'class':{'productPrice'}}) == None:
                        name = item.find("a", {'class':'product-name'}).text.strip()
                        price = "None"
                        specialprice= item.find('span', {'class':'productSpecialPrice'}).text
                        oldprice = item.find('span', {'class':'productOldPrice'}).text
                        img = str(item.find('img', {'class':'img-responsive'}).get('src'))
                    else:
                        name = item.find("a", {'class':'product-name'}).text.strip()
                        price = item.find('span',{'class':{'productPrice'}}).text
                        specialprice= "None"
                        oldprice = "None"
                        img = str(item.find('img', {'class':'img-responsive'}).get('src'))
                    records.append((name, price, specialprice, oldprice, img))
                count = count + 1
        create_csv(records)
        make_table_clean()
        fill_table()
        mydb.commit()
        cursor.close()
        print("======================================")
        print("Finished")
        print(f"{count} valid links")
        
    except Exception as e:
        print("Mission failed")
        print(e)
        print("======================================")
