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

import pandas as pd

exception_list=(TimeoutException,SessionNotCreatedException,ElementClickInterceptedException,WebDriverException,StaleElementReferenceException,NoSuchWindowException)
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)



DRIVER_PATH=''#add path to your web driver
driver = webdriver.Chrome(executable_path=DRIVER_PATH)

df = pd.DataFrame([])

def get_show_details():
    path = r''#add path where result.csv file from first script is stored
    df = pd.read_csv(path)
    for i in range(len(df)):
        data = df.iloc[i].to_dict()
        tickets(data)
        
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
     "show_format":t_det['show_format'],
     "status": 'PENDING',
     "localtz": '',
     "local_datetime": '',
     "ticketing_url":t_det['show_url'],
     "ticketing_available": 'available',
     "auditorium": t_det['Screen_no'],
     "available seats":t_det['Available_Seats'],
     "reserve seats":t_det['Reserve_Seats'],
     "social distancing seats":t_det['Social_distancing_seats'],
     "total seats":t_det['Total_Seats'],
     "category":t_det['Category'],
     "price":t_det['Price'],
     "movie_format": 'Standard'}    
     
    print(dataValues)
    

def tickets(data):
    global df
        
    try:
        driver.get(data['show_url'])
        data['Screen_no'] = driver.find_element_by_xpath('//*[@id="ctl00_Table1"]/tbody/tr[3]/td[2]/span').text[2:]
        data['Available_Seats'] = driver.find_element_by_class_name("ow-seats-available").text.split(':')[1]
    
        category_list=[]
        price_list = []                                                                                                                                     # ticket prices list with category and prices
        category = driver.find_elements_by_xpath('//table[@id="ctl00_ContentPlaceHolder1_OcisTicketsControl1_Table1"]/tbody/tr/td[3]')
        for c in category:
            category_list.append(c.text.split('@')[0])
            price_list.append(c.text.split('@')[1])
        data['Category'] = category_list
        data['Price'] = price_list
        
        if len(category)>1 :
            sel = Select(driver.find_element_by_xpath('//table[@id="ctl00_ContentPlaceHolder1_OcisTicketsControl1_Table1"]/tbody/tr[2]/td[2]/select'))
            sel.select_by_visible_text("1")
        else :            
            sel=Select(driver.find_element_by_xpath('//table[@id="ctl00_ContentPlaceHolder1_OcisTicketsControl1_Table1"]/tbody/tr/td[2]/select'))
            sel.select_by_visible_text("1")
           
    
        your_email = "srivastava0227@gmail.com"

        email = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_OcisTicketsControl1_txtEmail"]')
        email.clear()
        email.send_keys(your_email)
        confirm_email = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_OcisTicketsControl1_txtConfirmEmail"]')
        confirm_email.clear()
        confirm_email.send_keys(your_email)
    
        driver.find_element_by_xpath('//*[@id="ctl00_Button1"]').click()

        try:
            seat_matrix = driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_OcisSelectingSeatsControl1_Table1"]/tbody')
            seat_rows = seat_matrix.find_elements_by_class_name('ow-client-row')
            reserved_count = 0
            dist_count = 0
            for row in seat_rows:
                seat_list = row.find_elements_by_class_name('ow-client-cell-red')
                dist_list = row.find_elements_by_class_name('ow-client-cell')
                reserved_count+= len(seat_list)
                dist_count+= len(dist_list)
            
            data['Reserve_Seats']=reserved_count
            data['Social_distancing_seats'] = dist_count
            data['Total_Seats']=reserved_count + int(data['Available_Seats'])+dist_count
        except :
            data['Reserve_Seats'] = 'NA'
            data['Total_Seats'] = 'NA'
            data['Social_distancing_seats'] = 'NA'
        print_values(data)
        df=df.append(data,ignore_index=True)
        df.index+=1
    except :
        print("Show not available now")
  
           
    
if __name__=='__main__':
    get_show_details()
    df.to_csv('final.csv',index=False)
    driver.quit()