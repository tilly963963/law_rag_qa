import logging
import falcon

from config import LLM_NAME
from libs.utils import openai_client
from ollama import Client

logger = logging.getLogger(__name__)



QA_SYS_WHOLE_RULE = """
你的任務是閱讀理解文章，並根據文章回答問題。輸入格式如下：

法規名稱：<法規名稱>
<條文>
內文：<text>

問題：<question>

根據上述法規內容，簡潔和專業的回答問題，答案不允許編造，
如果無法從中得到答案，請回答“文章中無法得知答案，請您嘗試修改問題內容後重新提問”。
"""


QA_SYS_MSG = """你的任務是根據法規知識庫資料與使用者問題提供“答案”和“法規來源”，“答案”是指法規知識庫中與問題最相關的法條內容;“法規來源”是指其對應的法規名稱、法規章節、完整法條。

法規知識庫的資料是由數個與問題相關的法規知識點組成，當中的法規知識點是依照相關性排序，與問題越相關的知識點排在越前面。以n個法規知識點為例，格式如下：
```
***排序第1名相關的法規知識點***
法規名稱：<法規名稱>
法規章節：<法規章節>
法條內容：
<法條>：<text>

***排序第2名相關的法規知識點***
法規名稱：<法規名稱>
法規章節：<法規章節>
法條內容：
<法條>：<text>

***排序第3名相關的法規知識點***
法規名稱：<法規名稱>
法規章節：<法規章節>
法條內容：
<法條>：<text>

...

***排序第n名相關的法規章節***
法規名稱：<法規名稱>
法規章節：<法規章節>
法條內容：
<法條>：<text>
```

問題：<question>
注意事項：
1. 根據法規知識庫資料與問題提供“答案”和“法規來源”，“答案”是指法規知識庫中與問題最相關的法條內容;“法規來源”是指其對應的法規名稱、法規章節、完整法條。
2. “答案”與“法規來源”不允許編造。如果無法從法規知識庫資料得到答案，請回答“無法得知答案，請您重新提問”。
3. 回答請使用繁體中文
4. 回答請注意排版
"""
class LLMModelCloud:
    def __init__(self):
        logger.info("Use cloud LLM model")
        HOST = "http://155.248.164.12:7869"

        self.ollama_client = Client(host=HOST, timeout=300)

    def qa(self, sys_msg: str, user_msg: str):
        try:
            completion = openai_client.chat.completions.create(
              model=LLM_NAME,
              messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
              ],
              temperature=0
            )
            logger.debug("sys_msg: {}\n\nuser_msg: {}".format(sys_msg, user_msg))
            ans = completion.choices[0].message.content
        except Exception as e:
            logger.exception(e)
            raise falcon.HTTPServiceUnavailable("LLM API is not available.")
    
        return ans

    def ollama_qa(self, sys_msg: str, user_msg: str):
        logger.info("Use ollama_qa")
        
        response = self.ollama_client.chat(
        # model=LLM_NAME,
        model= 'Llama3-Taiwan-70b-Instruct-q5_k_m.gguf:latest',
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg}
        ],
        stream=False,
        options= {"seed":42}
        )
        ans = response["message"]["content"]
        return ans



