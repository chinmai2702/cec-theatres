from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException 
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import NoSuchElementException
import urllib.parse as urlparse
from urllib.parse import parse_qs
import pandas as pd

exception_list=(TimeoutException,SessionNotCreatedException,ElementClickInterceptedException,WebDriverException,StaleElementReferenceException,NoSuchWindowException)
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)

DRIVER_PATH=''#add_path_to_your_web_driver
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
driver.get('https://cectheatres.com/theatres/')
driver.maximize_window()

df=pd.DataFrame([])
data = {}
date_list = ["20201125"]#add_dates_of_which_you_want_to_extract_details_in_yyyymmdd_format

#to get the details of theatre
def get_theatre_details(theatre):
        driver.get(theatre)
        t_s = {"IA":"IOWA","MN":"MINNESOTA","NE":"NEBRASKA","WI":"WISCONSIN"}
        full_address = driver.find_element_by_xpath('//*[@id="main-wrapper"]/section[2]/div/div/div[1]/div/div[2]/div/h2').text
        data['Theatre-url'] = theatre
        data['Theatre-id'] = theatre.split('/')[4]
        data['Theatre-name']=driver.find_element_by_xpath('//*[@id="main-wrapper"]/section[1]/div/div/div/div/h1').text
        data['Theatre-address']=full_address.split(',')[0]
        data['Theatre-city']=full_address.split(',')[1]
        state=(full_address.split(',')[2].split()[0]).upper()
        data['Theatre-state'] = t_s[state]
        data['Theatre-zipcode']=full_address.split(',')[2].split()[1]
        return data
      

def start():
    url_list = geturls()
    for theatre in url_list:
        theatre_details = get_theatre_details(theatre)
        get_date_list(theatre_details)   
# to loop through each date entered by user        
def get_date_list(theatre_details):
    try:
        
        dates=WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//*[@id='outer-dropdown']/option")))
        for date in dates:
            WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="main-wrapper"]/section[3]/div/div/div/div[1]/div[2]/form/div/button/span[2]/span'))).click()
            if date.get_attribute('value') in date_list:
                date.click()
                get_movie_details(theatre_details,date.get_attribute('value'))
       
    except :
        print("theatre currently closed")
#to return the time in 24-hour format        
def get_time(t):
    x = t.split(' ')[0]
    if "PM" in t:
        if x.split(':')[0] == "12":
            res = x
        else:
            k = int(x.split(':')[0])+12
            res = str(k)+":"+x.split(':')[1]
    else:
        if x.split(':')[0] == "12":
            res = "00:"+x.split(':')[1]
        else:
            res = x
    return res[:5]

def print_values(t_det):
    dataValues = {
     "id": t_det['id'],
     "theater_id": t_det['Theatre-id'],
     "theater_name": t_det['Theatre-name'],
     "address": t_det['Theatre-address'],
     "city": t_det['Theatre-city'],
     "state": t_det['Theatre-state'],
     "zipcode": t_det['Theatre-zipcode'],
     "movie_id": t_det['movie_id'],
     "movie_name": t_det['movie_name'],
     "rating": t_det['movie_rating'],
     "runtime": t_det['movie_duration'],
     "amenities": '',
     "date": t_det['Date'] ,
     "time": t_det['movie_time'],
     #"session_id":t_det['session_id'],
     "show_format":t_det['show_format'],
     "status": 'PENDING',
     "localtz": '',
     "local_datetime": '',
     "ticketing_url":t_det['show_url'],
     "ticketing_available": 'available',
     "auditorium": '',
     "movie_format": 'Standard'}
    print(dataValues)

        
        
def get_movie_details(theatre_details,date):
        global df
        movie_list = []
        movie_list = driver.find_element_by_xpath('//*[@id="main-wrapper"]/section[4]/div/div/div').find_elements_by_xpath('//div[@class="black-box new-red-box hr-line schedule-dates date-'+date+'"]')

        for movie in movie_list :
            data['Date'] = date[:4]+"-"+date[4:6]+"-"+date[6:]
            data['movie_duration'] =  movie.find_element_by_css_selector('div:nth-child(1) > div > div > ul > li:nth-child(1)').text
            data['movie_url'] = movie.find_element_by_css_selector('div:nth-child(1) > div > div > h3 > a').get_attribute('href')
            data['movie_id'] = (data['movie_url'].split("/"))[4]
            data['movie_name'] = movie.find_element_by_css_selector('div:nth-child(1) > div > div > h3 > a').text
            if 'LDX' in data['movie_name']:
                data['show_format'] = "LDX Screen"
            else:
                data['show_format'] = "Standard"
            data['movie_rating'] = movie.find_element_by_css_selector('div:nth-child(1) > div > div > ul > li:nth-child(2)').text 
            shows = movie.find_element_by_css_selector('div:nth-child(2) > div > div.mobile-show-movie.hidden-md.hidden-lg > div > div.col-xs-8.col-sm-9.col-md-9.col-lg-9 > div > ul').find_elements_by_tag_name('li')
            for show in shows:
                t = show.find_element_by_tag_name('a').get_attribute('textContent')
                data['movie_time'] = get_time(t)
                data['show_url'] = show.find_element_by_tag_name('a').get_attribute('href')
                parsed = urlparse.urlparse(data['show_url'])
                data['id'] = parse_qs(parsed.query)['perfix'][0]
                theatre_details.update(data)
                print_values(theatre_details)
                df=df.append(theatre_details,ignore_index=True)
                df.index+=1
    
    
    
def geturls():
    link_list=[]
    theatre_l = driver.find_element_by_xpath('//*[@id="all-movie"]/div/div/div').find_elements_by_class_name('theatre-box')
    for theatre in theatre_l:
        link_list.append(theatre.find_element_by_class_name('h1-link').get_attribute('href'))
    return link_list

if __name__=='__main__':
    start()
    df.to_csv ("result.csv",index=False)
    driver.quit()