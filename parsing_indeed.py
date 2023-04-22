#!/usr/bin/env python
# coding: utf-8

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service #as ChromeService
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import pandas as pd
from tqdm.notebook import tqdm
import datetime as dt

driver = webdriver.Chrome(ChromeDriverManager().install())

# назначаем список переменных для всех региональных доменов indeed
indeed_regions = ['ar.', 'au.', 'at.', 'bh.', 'be.', 'br.', 'ca.', 'cl.', 'cn.', 'co.',
                  'cr.', 'cz.', 'dk.', 'ec.', 'eg.', 'fi.', 'fr.', 'de.', 'gr.', 'hk.',
                  'hu.', 'in.', 'id.', 'ie.', 'il.', 'it.', 'jp.', 'kw.', 'lu.',
                  'malaysia.', 'mx.', 'ma.', 'nl.', 'nz.', 'ng.', 'no.', 'om.', 'pk.',
                  'pa.', 'pe.', 'ph.', 'pl.', 'pt.', 'qa.', 'ro.', 'sa.', 'sg.',
                  'za.', 'kr.', 'es.', 'se.', 'ch.', 'tw.', 'th.', 'tr.', 'ua.', 'ae.',
                  'uk.', 'uy.', 've.', 'vn.', '']

offers = ['junior+data+analyst','junior+data+scientist']

job_data = []

# пишем функцию закрытия поп апов, будем использовать ее в основной функции, поскольку на indeed`е поп апы могут всплывать случайно
def close_popup():
  try:
      driver.find_elements(By.XPATH, "//button[@class='icl-CloseButton icl-Modal-close']").click()
  except:
      pass

# дефайним основную функцию
def main_parser(url, output_variable):

    driver.get(url)
    close_popup()
    # инициализация счетчика шагов цикла
    count = 0

    while True:

        close_popup()
        # находим все карточки на странице
        job_cards = driver.find_elements(By.XPATH, '//a[@class = "jcs-JobTitle css-jspxzf eu4oa1w0"]')
        # проходим циклом по всем карточкам вакансий
        for jc in job_cards:
            try:
                close_popup()
                jc.click()
            except:
                close_popup()
                driver.execute_script("arguments[0].click();", jc)
            close_popup()
            sleep(5)
            
            # забираем интересующую информацию со страницы
            ## ссылка на вакансию
            try:
                link = driver.find_element(
                    By.XPATH, '//a[@class = "css-1ublnu3 e8ju0x50"]').get_attribute('href')
            except:
                link = jc.get_attribute('href')
            close_popup()
            ## название вакансии
            try:
                title = jc.text
            except:
                title = driver.find_element(
                    By.XPATH, '//h1[@class = "icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title"]').text.strip().split('\n')
            close_popup()                  
            ## название компании
            try:
                company = driver.find_element(
                        By.XPATH, '//div[@class = "css-1h46us2 eu4oa1w0"]').text.strip().split('\n')
            except:
                company = None
            close_popup()
            ## место работы
            try:
                location = driver.find_element(
                    By.XPATH, '//div[@class = "css-6z8o9s eu4oa1w0"]').text.strip().split('\n')
            except:
                location = None
            close_popup()
            ## описание вакансии
            try:
                description = driver.find_element(
                    By.XPATH, '//div[@id = "jobDescriptionText"]').text.strip().split('\n')
            except:
                description = 'not_indicated'
            close_popup()
            ## зарплата, если указана
            try:
                salary = driver.find_element(
                    By.XPATH, '//span[@class = "css-2iqe2o eu4oa1w0"]').text.strip().split('\n')
            except:
                salary = None
            close_popup()

            # формируем словарь того, что мы забрали
            data = {'title':title, 
                    'company':company[0], 
                    'country':f'{region}',
                    'location':location[0],
                    'salary':salary,
                    'source':'indeed',
                    'link':link,
                    'date':dt.datetime.today().strftime("%d-%m-%Y"),
                    'company_field':None,
                    'description':description,
                    'skills':None,
                    'job_type': 'remote/hybrid' if ('remote' in location[0].lower()
                                or 'hybrid' in location[0].lower())
                                else ('contract' if 'contract' in location[0].lower()
                                else 'full-time')
                    }
            # складываем все в назначенную переменную
            output_variable.append(data)
            # скроллим дальше
            jc.location_once_scrolled_into_view

        # проверяем есть ли кнопка "следующая страница" и нажимаем, если есть
        try:
            next_button = driver.find_element(By.XPATH, '//a[@data-testid="pagination-page-next"]')
            next_button.click()
        except:
            print(f'Цикл завершен успешно, всего собрано {len(output_variable)} вакансий')
            break # останавливаем скраппинг, если кнопки нет

        # увеличиваем счетчик на каждой итерации
        count += 1
        # вызываем исключение на 20-й итерации
        if count == 20:
            raise Exception('Достигнут предел числа итераций - нужно увеличить количество итераций' 
                            if next_button else 'Достигнут предел числа итераций - страницы закончились (бесконечный цикл)')

for offer in offers:
    for region in tqdm(indeed_regions):
        
        url = f'https://{region}indeed.com/jobs?q={offer}&fromage=1&start=0'

        main_parser(url, job_data)

# закрываем браузер
driver.quit()

# напишем словарь соответствия доменов названиям стран
domen_country = {'ar.':'Argentina',
    'au.':'Australia',
    'at.':'Austria',
    'bh.':'Bahrain',
    'be.':'Belgium',
    'br.':'Brazil',
    'ca.':'Canada',
    'cl.':'Chile',
    'cn.':'China',
    'co.':'Colombia',
    'cr.':'CostaRica',
    'cz.':'CzechRepublic',
    'dk.':'Denmark',
    'ec.':'Ecuador',
    'eg.':'Egypt',
    'fi.':'Finland',
    'fr.':'France',
    'de.':'Germany',
    'gr.':'Greece',
    'hk.':'HongKong',
    'hu.':'Hungary',
    'in.':'India',
    'id.':'Indonesia',
    'ie.':'Ireland',
    'il.':'Israel',
    'it.':'Italy',
    'jp.':'Japan',
    'kw.':'Kuwait',
    'lu.':'Luxembourg',
    'malaysia.':'Malaysia',
    'mx.':'Mexico',
    'ma.':'Morocco',
    'nl.':'Netherlands',
    'nz.':'NewZealand',
    'ng.':'Nigeria',
    'no.':'Norway',
    'om.':'Oman',
    'pk.':'Pakistan',
    'pa.':'Panama',
    'pe.':'Peru',
    'ph.':'Philippines',
    'pl.':'Poland',
    'pt.':'Portugal',
    'qa.':'Qatar',
    'ro.':'Romania',
    'sa.':'SaudiArabia',
    'sg.':'Singapore',
    'za.':'SouthAfrica',
    'kr.':'SouthKorea',
    'es.':'Spain',
    'se.':'Sweden',
    'ch.':'Switzerland',
    'tw.':'Taiwan',
    'th.':'Thailand',
    'tr.':'Turkey',
    'ua.':'Ukraine',
    'ae.':'UnitedArabEmirates',
    'uk.':'UnitedKingdom',
    '':'UnitedStates',
    'uy.':'Uruguay',
    've.':'Venezuela',
    'vn.':'Vietnam',
    }

# записываем собранные данные в итоговый датафрейм
df = pd.DataFrame(job_data)
# преобразуем некоторые колонки
df['salary'] = df['salary'].apply(lambda x: x if x == None else ''.join(x))
# в колонке country меняем домены на названия стран
df['country'] = df['country'].map(domen_country)
# удаляем дубликаты
df.drop_duplicates(subset=['title', 'company', 'location'], keep='first',inplace=True)

# опеределяем путь сохранения csv
save_path = 'C:\\Users\\maste\\Downloads'

# выгрузка csv
df.to_csv(f'{save_path}\\indeed_parsing_output {dt.datetime.today().strftime("%d-%m-%Y")}.csv',
         index=False)