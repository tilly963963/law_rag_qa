import os
import json
import requests
import streamlit as st
import logging
import threading
import ast

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

st.set_page_config(layout="wide")
init_logging()
logger = logging.getLogger(__name__)
os.environ["HTTP_PROXY"] = ""

def run_qa(sentence, hits, algo, qa_holder):
    with qa_holder:

            with st.spinner("🤖 思考中..."):
            

                try:
                    data = {
                        "sentence": sentence,
                        "snippets": [i['index'] for i in hits],
                        "algorithm": algo,
                        "filename":[i["filename"] for i in hits],
                        "full_title_texts":[i["full_title_text"] for i in hits]
                    
                    }
                
                
                    ans = requests.post(f"{BACKEND_URL}/llm", json=data).json()
                    qa_dt = ans["dt"]

                except:
                    ans = ""
                    qa_dt = -1
                st.session_state.ans = ans
                st.session_state.qa_dt = qa_dt 
                
                qa_time = "🤖 總結如下 (耗時：{} 秒)".format(st.session_state.qa_dt)
                qa_holder.write(":red[{}]".format(qa_time))
                qa_holder.write(st.session_state.ans["response"])
                qa_holder.write("---")




def render_tab(sentence, predictions, algo):
    hits = predictions["hits"]
    dt = predictions["time_sec"]
  
    if not hits:
        st.markdown("無相關知識點")
    else:
        # with algo_tab:
            st.markdown("""
                <style>
                .small-font {
                    font-size:15px; color: gray;
                }
                </style>
            """, unsafe_allow_html=True)
            qa_holder = st.container()
            qa_holder.empty()

            search_time = "搜尋結果 (耗時：{:.4f} 秒)".format(dt)
            st.markdown(":red[{}]".format(search_time))
            
            for i, pred in enumerate(hits):
                with st.container():
                    fn = pred["filename"]
                    text = pred["text"]
                    full_title_text = pred["full_title_text"]


                    source = pred["source"] # include source and title -> first_title/second_title/source
                    score = pred["dist"]


                    meta_title = ast.literal_eval(str(pred["meta"]))['title']
                    meta_label = ast.literal_eval(str(pred["meta"]))["label"] 
            
                    meta_label_str = meta_label
                    if score > 0:
                        score = round(score, 4)
                    s_color = "blue" if score <= 0.15 else "red"
                    info = source
                 
                    new_text = f":gray[{full_title_text}]"
                    new_info = f":green[{info}]"
                    
                    
                    text_color = f':gray[{full_title_text}]'

                    if source != 'pass':
                        source_color = source.split(',')[:-1]
                        for i in source_color:
                            text_color = text_color.replace(i,f':green[{i}] ')
                    
                    if meta_label_str=='upload_data':
                        st.markdown("**{}** / :{}[{}]".format( fn, s_color, score))

                    elif meta_title=='pass':
                        st.markdown("**{}** / **{}** / :{}[{}]".format(meta_label_str, fn, s_color, score))

                    else:
                        st.markdown("**{}** / **{}** / :green[{}] / :{}[{}]".format(meta_label_str, fn, meta_title, s_color, score))

                    st.markdown(text_color.replace('\n','  \n'))

            run_qa(sentence, hits, algo, qa_holder)
def click_button(question, label, upload_res):
 
    st.session_state.clicked = True

    if st.session_state.using_upload_file and (upload_res is False):#(uploaded_file is  None):
        st.warning('請上傳資料', icon="⚠️")
        st.session_state.clicked = False
   
    if st.session_state.using_db and (label == []):
        st.warning('請選擇機構', icon="⚠️")
        st.session_state.clicked = False

    if not question:
        st.warning('請輸入問題', icon="⚠️")
        st.session_state.clicked = False

    if not st.session_state.using_upload_file and not st.session_state.using_db:
        st.warning('請 上傳資料 或是 選擇機構', icon="⚠️")
        st.session_state.clicked = False

def input_enable():
    st.session_state.clicked = False
    st.rerun()

#!不確定哪些要寫在clicked裏面 結果相同
if __name__ == "__main__":
    st.title("智能化勞動法律助手")
    BACKEND_URL = "http://pycon-law-rag-backend:15012"

    # BACKEND_URL = os.getenv("BACKEND_URL", "http://172.20.10.2:15009")

    import pdfplumber


    if 'clicked' not in st.session_state:
        st.session_state.clicked = False


    ## keep api data  ##
    if 'pred_res' not in st.session_state:
        st.session_state.pred_res = None

    if 'upload_res' not in st.session_state:
        st.session_state.upload_res = False

    if 'label' not in st.session_state:
        st.session_state.label = []
        
    with st.container():
        using_upload_file = st.checkbox('Uploaded file', key ='using_upload_file')

        if using_upload_file:

            uploaded_files = st.file_uploader("Choose a file", type="pdf", accept_multiple_files=True)
            dataloader_datas=[]
    
            if uploaded_files:
                for uploaded_file in uploaded_files:

                    st.success("Uploaded the file")
                    text =''
                    with pdfplumber.open(uploaded_file) as file:
                        all_pages = file.pages
                        for page in all_pages:
                            text = text + page.extract_text()
         
                    dataloader_data = {"file_name":uploaded_file.name,"text":text}
                    dataloader_datas.append(dataloader_data)
                data = {'uploaded_files_data':dataloader_datas,'asd':'ddd'}
                st.session_state.upload_res = requests.post(f"{BACKEND_URL}/dataloader", json=data).json()
            else:
                st.session_state.upload_res=False
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
    with st.container():
        using_db = st.checkbox('Using db', key ='using_db')
    
        if using_db:
      
            st.multiselect("法規類別", options=label_data.keys(), default=label_data.keys(), key ='label')
        
        
    sentence = st.text_input(
                "輸入問題", placeholder="", key="question", disabled=st.session_state.get("clicked")
            )

    
    mergedata = False #! status
    uploaddata = False #! status

    # st.snow()
    st.button('Submit', on_click=click_button, disabled=st.session_state.get("clicked"), args=(st.session_state.question,st.session_state.label ,st.session_state.upload_res))#只要是st.session_state就吃得進去 不一定要寫成arg參數嗎？
    if  st.session_state.clicked:

        with st.spinner("🤖 搜尋中..."):
            
            if using_upload_file and st.session_state.upload_res:#!是否要寫在clicked裏面？？
                uploaddata = st.session_state.upload_res["predictions"]["uploaddata"]["hits"]
                if using_db:
                    mergedata = True


            logger.info("inside st.session_state.clicked {}".format(st.session_state.clicked ))

            search_data = {"sentence":sentence,"label":st.session_state.label,"file":[],"uploaddata":uploaddata,"mergedata":mergedata}
   

            st.session_state.pred_res = requests.post(f"{BACKEND_URL}/search", json=search_data).json()
            # st.write(st.session_state.pred_res ) 
            
            hits = st.session_state.pred_res["predictions"]["語意搜尋"]#["hits"]

    algo = "語意搜尋"
    if st.session_state.pred_res:
        # st.write(hits) 
        render_tab(sentence,st.session_state.pred_res["predictions"]["語意搜尋"], algo)
 
        if st.session_state.clicked: #開放label與問題輸入
            input_enable()
    
