import os
import json
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup
# from libs.embedding import EmbModelCloud

logger = logging.getLogger(__name__)

r = requests.get("https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=N0020017")
soup = BeautifulSoup(r.text, 'html.parser')

# results = soup.find('div', attrs={'class':'law-reg-content'})
# logger.info("file_name: {}".format(file_name))
# logger.info("results: {}".format(results))

# find_titles = soup.find_all('div', attrs={'class':'h3 char-2'})
# for title in find_titles:
#     title.
rows = soup.find_all('div', attrs={'class':'h3 char-2'})

# rows = soup.find_all('div', attrs={'class':'row'})
for row in rows:
    # logger.info("===")
    print('---')
    print('row = ',row)
    tests = row.find_next_siblings()#[#-1].get('h3 char-2')#.find('h3 char-2')#.find_parent()#.find_all('h3 char-2')#.find_previous_siblings()
    # print(len(tests))
    # print(tests)
    for test in tests:
       
        test = BeautifulSoup(str(test), 'lxml')
      
        if test.find('div', attrs={'class':'h3 char-2'}):
            break
        # if 'h3 char-2' in cc:
        #     break
        # cc = BeautifulSoup(str(cc), 'lxml')
        number = test.find('div', attrs={'class':'col-no'}).text
        article = test.find('div', attrs={'class':'law-article'}).text.replace('\n','')
                # article_emb = self.emb_model.encode(article)
                # data = {'file_name':file_name ,'number':number, 'article':article ,'article_emb':article_emb, 'link':data["link"], 'meta':data["meta"]}
                # save_data.append(data)
        print(number)
        # print(cc)
    #     # test = BeautifulSoup(test, "html.parser")
        # test =  BeautifulSoup(test, "lxml")
    #     ll = test.get('div')#.find('div', attrs={'class':'row'})#[-1]
    #     # print(ll)
        # print(test)
    # logger.debug("test: {}".format(test))

            # if find_title:
            #     numbers = ''
            #     articles = ''

                
            #     for result in find_title:
            #         logger.info("result: {} ".format(result))

            #         ss = result.find_next_siblings("col-no")
            #         logger.info("ss: {} ".format(ss))
            #         kk = result.find_next_siblings("law-article")
            #         logger.info("ss: {} ".format(kk))
            #         numbers = numbers +','+ result.find('div', attrs={'class':'col-no'}).text
            #         articles = articles + result.find('div', attrs={'class':'law-article'}).text.replace('\n','')
            #     article_emb =99#self.emb_model.encode(articles)
            #     data = {'file_name':file_name ,'number':numbers, 'article':articles ,'article_emb':article_emb, 'link':data["link"], 'meta':data["meta"]}
            #     save_data.append(data)

            # else:
        #     for result in results.find_all('div', attrs={'class':'row'}):
        #         number = result.find('div', attrs={'class':'col-no'}).text
        #         article = result.find('div', attrs={'class':'law-article'}).text.replace('\n','')
        #         article_emb = self.emb_model.encode(article)
        #         data = {'file_name':file_name ,'number':number, 'article':article ,'article_emb':article_emb, 'link':data["link"], 'meta':data["meta"]}
        #         save_data.append(data)
        # except requests.exceptions.RequestException as e:
        #     print(e)
        
        # return save_data

      