import os
import json
import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List
import math
import requests
from bs4 import BeautifulSoup
from libs.embedding import EmbModelCloud
# from ollama import Client
logger = logging.getLogger(__name__)

class ParserHtml:
    def __init__(self):
        self.emb_model = EmbModelCloud()
        HOST = "http://155.248.164.12:7869"
        # self.client = Client(host=HOST)
    def get_url_data(self, root_url):
        title_link = []
        prefix_url = 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode='

        try:
            r = requests.get(root_url) #將此頁面的HTML GET下來

            soup = BeautifulSoup(r.text,"html.parser")
            logger.info("soup: {}".format(soup))

            rule = soup.find("div", {'class': 'law-result'})
            rule = rule.text.replace(' ','').replace('\n','').replace('\r','')
            label = rule.split('＞')[-1]
            table = soup.find("table", {'class': 'table table-hover tab-list tab-central'})

            data={}
            for row in table.tbody.find_all('tr'):
                columns = row.find_all('td')
                raw_link = columns[2].a['href']
                logger.info("title: {}".format(columns[2].a['title']))
  
                PCode = raw_link.split("?PCode=")[1]

                link = prefix_url + PCode
        
                # data = {'file': columns[2].a['title'] , 'link':link, 'raw_link': raw_link, 'meta':{'label':rule}}
                data[columns[2].a['title']]= {'file': columns[2].a['title'],'link':link, 'raw_link': raw_link, 'meta':{'label':label}}
                
                # title_link.append(data)

        except requests.exceptions.RequestException as e:
            print(e)

        return data
    def get_llm_summary(self, text):
        response = self.client.chat(
            # model="ycchen/breeze-7b-instruct-v1_0:latest",
            # model="gemma2:27b",
#
            model="qwen2:72b",


            messages=[
                    {
                    "role": "system",
                    "content": "你是一個專業的勞工局的智能小幫手，請將以下法規進行精簡的總結，請勿編造，字數在200字以內，請使用繁體中文。",
                    },
                    {
                        "role": "user",
                        "content": text+'\n\n總結：'
                    },
            ], stream=False)
            
        prompt_eval_count = response["prompt_eval_count"]

        eval_count = response["eval_count"]

        ans = response["message"]["content"]
        return ans ,prompt_eval_count ,eval_count
    def get_article(self, file_name, data):
        try:
            r = requests.get(data["link"])
            soup = BeautifulSoup(r.text, 'html.parser')

            results = soup.find('div', attrs={'class':'law-reg-content'})
            logger.info("file_name: {}".format(file_name))
            # logger.info("results: {}".format(results))

            save_data = []
            if results is None:
                logger.info("file_name: {} is pass".format(file_name))

                return None

            if soup.find('div', attrs={'class':'h3 char-2'}):
                full_text = ''
                accumulative_article = 0
                for title in soup.find_all('div', attrs={'class':'h3 char-2'}):
                    rows = title.find_next_siblings()
                    char_2_title=''
                    char_3_title=''
                    char_4_title=''
                    number=''
                    logger.info("title: {}".format(title))
                    
                    
                    data["meta"]['title']=title
                    split=False
                    article=''
                    for row in rows:
                    
                        row = BeautifulSoup(str(row), 'lxml')
                    
                        if row.find('div', attrs={'class':'h3 char-2'}):#第一章 總則
                           
                            # char_2_title= row.find('div', attrs={'class':'h3 char-2'}).text

                            # split = True
                            # article_emb=123
                            # data = {'file_name':file_name ,'number':number, 'article':char_3_title+char_4_title+article ,'article_emb':article_emb, 'link':data["link"], 'meta':data["meta"]}
                            # save_data.append(data)
                            break

                        if row.find('div', attrs={'class':'h3 char-3'}):#第一節 xx
                            char_3_title = row.find('div', attrs={'class':'h3 char-3'}).text.lstrip(' ').rstrip(' ')
                            logger.info("char_3_title: {}".format(char_3_title))
                            
                            # save_char_3_title = char_3_title
                            # continue
                            article = article+'\n'+char_3_title

                        if row.find('div', attrs={'class':'h3 char-4'}): #第一款 xX
                            logger.info("row: {}".format(row))

                            char_4_title = row.find('div', attrs={'class':'h3 char-4'}).text.lstrip(' ').rstrip(' ')
                            # continue
                            logger.info("char_4_title: {}".format(char_4_title))
                            article = article+'\n'+char_4_title


                        if row.find('div', attrs={'class':'row'}): #第1條

                            number = number+row.find('div', attrs={'class':'col-no'}).text+','
                            number = number.replace('本條文有附件','').lstrip(' ').rstrip(' ')
                        
                            article = article+'\n'+row.find('div', attrs={'class':'col-no'}).text.replace('本條文有附件','')+'：'+row.find('div', attrs={'class':'law-article'}).text.replace('\n','')


                    # if not split:
                    article = article.lstrip('\n').rstrip('\n')
                    article = article.lstrip(' ').rstrip(' ')
                    article = article.lstrip('　').rstrip('　')

                    # data = {'file_name':file_name ,'title':title.text,'char_3_title':char_3_title,'char_4_title':char_4_title,'number':number, 'article_len':article ,'article_emb':article_emb,'article':len(article), 'link':data["link"], 'meta':data["meta"]}
                    data["meta"]['title'] = 'pass'
                    # if len(article) < 100:
                    #     accumulative_article = accumulative_article + article
                    #     keep_context = file_name+'\n'+title.text+'\n'+article
                    #     keep_title=title.text
                    #     keep_file_name = file_name
                    #     keep_article_len = len(article) 
                    #     keep_article= article
                    title = title.text.lstrip(' ').rstrip(' ')
                    title = title.lstrip('　').rstrip('　')

                    full_text = full_text+'\n' + title+'\n' + article
                    full_text = full_text.lstrip('\n').rstrip('\n')

                    if len(article) < 1000:
                        # if keep_context:
                        #    context =  keep_context + context
                       
                        context = file_name + '\n' + title + '\n' + article
           
                  
                        article_emb = [0]#self.emb_model.encode(context)#[123]
                        # article_emb = [11]#self.emb_model.encode(context)#[11]# self.emb_model.encode(article)
                        data = {'file_name':file_name ,'title':title,'number':number, 'context':context,'article':article ,'text_len':len(article), 'article_len':len(article) ,'article_emb':article_emb, 'link':data["link"], 'meta':data["meta"]}
                        save_data.append(data)
                    else:
                        window_size = 1000
                        stride = 0

                        split_num = len(article)/ (window_size - stride)
                        for id,i in enumerate(range(math.ceil(split_num))):
                            logger.info(" {}".format(id))
                            
                            logger.info("{}, {}".format((window_size - stride)*i ,(window_size - stride)*i+window_size))

                            text = article[(window_size - stride)*i : (window_size - stride)*i+window_size]
                            logger.info("text len {}".format(len(text)))
                            text = text.lstrip('\n').rstrip('\n')
                            text = text.lstrip(' ').rstrip(' ')
                            text = text.lstrip('　').rstrip('　')
                            context = file_name+'\n'+title+'\n'+text
                            article_emb = [1]#self.emb_model.encode(context)#[123]
                            # article_emb = [11]#self.emb_model.encode(context)#[11]# self.emb_model.encode(article)

                            data = {'file_name':file_name ,'title':title,'number':number,'context':context, 'article':text ,'text_len':len(text) ,'article_emb':article_emb,'article_len':len(article), 'link':data["link"], 'meta':data["meta"]}
                            save_data.append(data)

                    count_filename=[]
                    llm_summary={}
                    llm_ans=''

                # logger.info("full_text_token {}".format(full_text_token))

                from transformers import AutoTokenizer
                # tokenizer = AutoTokenizer.from_pretrained("teknium/OpenHermes-2.5-Mistral-7B")
                # tokens = tokenizer.apply_chat_template(messages)
                logger.info("full_text_len {}".format(len(full_text)))
                
                llm_ans, full_text_token ,llm_summary_token = self.get_llm_summary(full_text)
                llm_ans =''
                full_text_token =''
                llm_summary_token=''
                
                logger.info("llm_ans {}".format(llm_ans))

                logger.info("full_text_token {}".format(full_text_token))
                
                logger.info("llm_summary_token {}".format(llm_summary_token))

                for i in range(len(save_data)):
                    save_data[i]['full_text'] = full_text
                    save_data[i]['full_text_token'] = full_text_token

                    save_data[i]['llm_summary']=llm_ans
                    save_data[i]['llm_summary_token']=llm_summary_token
                    

                            
                
            else: 
                
                numbers=''
                articles=''
                full_text = ''

                for result in results.find_all('div', attrs={'class':'row'}):
                    number = result.find('div', attrs={'class':'col-no'}).text
                    number = number.replace('本條文有附件','').lstrip(' ').rstrip(' ').lstrip('　').rstrip('　')

                    
                    article = result.find('div', attrs={'class':'law-article'}).text.replace('\n','')
                    # data = {'file_name':file_name ,'number':number, 'article':article ,'article_emb':article_emb,'article_len':len(article), 'link':data["link"], 'meta':data["meta"]}
                    # article_emb=[123]#self.emb_model.encode(article)#[123]
                    # data = {'file_name':file_name ,'title':title.text,'char_3_title':char_3_title,'char_4_title':char_4_title,'number':number, 'article_len':article ,'article_emb':article_emb,'article':len(article), 'link':data["link"], 'meta':data["meta"]}
                    numbers = numbers+number+','
                    article = article.lstrip('\n').rstrip('\n')
                    article = article.lstrip(' ').rstrip(' ')
                    article = article.lstrip('　').rstrip('　')
                    articles = articles +number+'：'+article+'\n'
                    context = file_name+'\n'+articles
                    full_text = full_text+number+'：'+article+'\n'
                    logger.info("row: len(context){}".format(len(context)))
                    continue_add = False
                    if len(context)<1000:#累加到一千字才存
                        continue
                        rows = result.find_next_siblings()
                        for row in rows:
                            logger.info(row)
                    
                            row = BeautifulSoup(str(row), 'lxml')
                            ll = row.find('div', attrs={'class':'line-0000 show-number'})
                            kk = row.find('div', attrs={'class':'line-0000'})
                            cc =row.find_all('line-0000 show-number')
                            dd =row.find_all('line-0000')
                            logger.info("row.find('div',cc {}".format(cc))
                            logger.info("row.find('div',dd {}".format(dd))
                            logger.info("row.find('div',ll {}".format(ll))
                            logger.info("row.find('div',kk {}".format(ll))

                            if ll or kk:

                                continue_add = True
                                break
                        if continue_add:
                            continue
                        else:#繼續累加
                            
                                article_emb = [11]#self.emb_model.encode(context)#[11]# self.emb_model.encode(article)
                                data = {'file_name':file_name ,'title':'pass','number':numbers,'context':context, 'article':articles , 'article_len':len(context) ,'article_emb':article_emb,'link':data["link"], 'meta':data["meta"]}
                                save_data.append(data) 
                                numbers=''
                                articles=''
                    else:
                        # article_emb = [11]#self.emb_model.encode(context)#[11]# self.emb_model.encode(article)

                        article_emb =[22]# self.emb_model.encode(context)#[11]# self.emb_model.encode(article)
                        data = {'file_name':file_name ,'title':'pass','number':numbers,'context':context, 'article':articles ,'text_len':len(context) , 'article_len':len(context) ,'article_emb':article_emb,'link':data["link"], 'meta':data["meta"],'full_text':''}
                        save_data.append(data) 
                        numbers=''
                        articles='' 
                            
                if   articles !='' : #剩下不足1000字的       
                        # article_emb = self.emb_model.encode(context)#[11]# self.emb_model.encode(article)
                        article_emb =[33]
                        data = {'file_name':file_name ,'title':'pass','number':numbers,'context':context, 'article':articles,'text_len':len(context)  , 'article_len':len(context) ,'article_emb':article_emb,'link':data["link"], 'meta':data["meta"],'full_text':''}
                        save_data.append(data) 
                        numbers=''
                        articles=''
                if save_data:
                    for i in range(len(save_data)):
                        save_data[i]['full_text'] = full_text
                    # if len(article) < 4000:
                    #     context = file_name+'/'+article
                    #     article_emb = self.emb_model.encode(context)#[11]# self.emb_model.encode(article)
                    #     data = {'file_name':file_name ,'title':'pass','number':number, 'article':article , 'article_len':len(article) ,'article_emb':article_emb,'link':data["link"], 'meta':data["meta"]}
                    #     save_data.append(data)
                    # else:
                    #     window_size=4000
                    #     stride = 2000
                    #     split_num = len(article)/ (window_size - stride)
                    #     for id,i in enumerate(range(math.ceil(split_num))):
                    #         logger.info(" {}".format(id))
                            
                    #         logger.info("{}, {}".format((window_size - stride)*i ,(window_size - stride)*i+window_size))

                    #         text = article[(window_size - stride)*i : (window_size - stride)*i+window_size]
                    #         logger.info("text len {}".format(len(text)))
                    #         context = file_name+'/'+text
                    #         article_emb = self.emb_model.encode(context)#[123]
                    #         data = {'file_name':file_name ,'title':'pass','number':number, 'article':text ,'text_len':len(text) ,'article_emb':article_emb,'article_len':len(article), 'link':data["link"], 'meta':data["meta"]}
                    #         save_data.append(data)
        except requests.exceptions.RequestException as e:
            print(e)
        
        return save_data

      