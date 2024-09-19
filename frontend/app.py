import os
import json
import requests
import streamlit as st
import logging
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
from io import StringIO
def init_logging():
    formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(levelname)s %(processName)s --- [%(threadName)s] %(name)s : %(message)s", "%Y-%m-%d %H:%M:%S")
    logger_level = int(os.getenv("LOGGER_LEVEL", logging.INFO))
    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)
    handlers = [ch]

    logging.basicConfig(level=logger_level, handlers=handlers)


init_logging()
logger = logging.getLogger(__name__)
os.environ["HTTP_PROXY"] = ""
# BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:15002")
# BACKEND_URL = "http://172.20.10.2:15002"

def click_button():
 
    st.session_state.clicked = True
def click_button2():
 
    st.session_state.clicked_2 = True
if __name__ == "__main__":
    st.title("知識庫創建")

    BACKEND_URL = "http://pycon-law-rag-backend:15012"
    
    import pdfplumber

    import streamlit as st
    
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
 
    if 'clicked_2' not in st.session_state:
        st.session_state.clicked_2 = False


    label_data = {
        # "組織目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010001",
        "勞動關係目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010002",
        "勞動保險目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010003",
        "勞動福祉退休目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010004",
        "勞動條件及就業平等目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010005",
        "職業安全衛生目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010006",
        "勞動檢查目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010007",
        "職業訓練目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010008",
        "就業服務目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010009",
        # "其他目":"https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010010"
    }
    label  = st.multiselect("主管機構", options=label_data.keys(), default=label_data.keys())

    file_names=[]
    file_datas =[]
    label_url=[]
    res = None
    data_2 ={}
    save_filename = st.text_input(
            "輸入檔名", placeholder=""
        )
    submit_ = st.button("Submit 1", on_click=click_button)
    st.write('Ministry_of_Labor_emb')

    if st.session_state.clicked :
        for i in label:
            label_url.append(label_data.get(i))
   
        url_data = {"url":label_url}
    
        res = requests.post(f"{BACKEND_URL}/url", json=url_data).json()
        article_datas = {}
        

        for url, datas in res["predictions"].items(): 
            for file_name, data in datas['hits'].items(): 
                file_names.append(file_name)
            file_datas.extend(datas)
        
        st.write(res["predictions"])
        if res:
            st.write('資料讀取')
            
        submit2 = st.button("Submit 2", on_click=click_button2)

        
        data_2 = {"file_data":res["predictions"],"save_filename":save_filename}
        # '
        res_2 = requests.post(f"{BACKEND_URL}/file", json=data_2).json()
        if res_2:
            st.write('資料完成下載')   
            
            st.session_state.clicked = False
            st.session_state.clicked_2 = False

# docker run -it --rm -v $PWD:/app -p 15011:8501 poc-docqa-ui:19d09e4 bash
# streamlit run app.py
# docker run -it --rm -v $PWD:/app -p 15019:8501  pycon-law-rag-frontend:fc17fe2 bash
# streamlit run app.py --global.disableWidgetStateDuplicationWarning=true
   