import os
import json
import logging
import pandas as pd
from typing import List
import ast
import re
# from libs.abstract_search import AbstractSearch, SearchResult
import copy

from config import DB_FILENAME
try:
    import chromadb
except RuntimeError:
    import sys
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules["pysqlite3"]
    import chromadb
from chromadb import Settings

logger = logging.getLogger(__name__)

VECTOR_DB_NAME = "pycon_law_rag"
DIST_TYPE = "cosine"
DIST_THRESHOLD = float(os.getenv("DIST_THRESHOLD", 0.2))
from dataclasses import dataclass, field
from typing import List
import time

@dataclass
class SearchResult:
    """
    required: index, filename, text, query
    """
    index: int  # index in source dataframe
    filename: str
    text: str    # 段落文本內容
    query: str   # origin query
    source: str = ""  # 條目
    # page: int = -1    # 頁數
    dist: float = -1  # search distance / score
    full_text : str = ""
    full_title_text  : str = ""
    meta: dict = field(default_factory=lambda : {})  # meta data，其餘想放的資訊

class AbstractSearch:
    def need_emb(self) -> bool:
        # 是否為需要embedding的演算法
        raise falcon.HTTPNotFound(title="need_emb() not implemented")

    def get_name(self) -> str:
        # 回傳該方法的名稱
        raise falcon.HTTPNotFound(title="get_name() not implemented")

    def query(self, sentence: str, **kwargs) -> List[SearchResult]:
        raise falcon.HTTPNotFound(title="query() not implemented")
class VectorSearch(AbstractSearch):
    def __init__(self,model_name):
        logger.info(f"VectorSearch model_name: {model_name}")

        KG_FILE = './Ministry_of_Labor_emb_gpt_bge_0723.csv'

        logger.info("Build knowledge...from {}".format(KG_FILE))

        # load data
        self.df = pd.read_csv(KG_FILE)
        

        self.df["is_upload_data"]=False
        self.df.reset_index(drop=True, inplace=True)

        logger.info(f"knowledge data shape: {self.df.shape}")

        # build vector db
        self.db_client = chromadb.Client()
        try:
            self.db_client.delete_collection(VECTOR_DB_NAME)
        except:
            pass
        logger.info(f"db_client create")

        self.collection = self.db_client.create_collection(
            VECTOR_DB_NAME,
            metadata = {
                "hnsw:space": DIST_TYPE,
             
                 "hnsw:construction_ef": 128,
                "hnsw:search_ef": 128,
                "hnsw:M": 128,
            }
        )
        logger.info(f"get_collecttion_data  model_name:{model_name}")

        ids, docs, embs, metas = self.get_collecttion_data(self.df, False, model_name)
     
    
        try:
            self.collection.add(
                ids=ids,
                documents=docs,
                embeddings=embs,
                metadatas=metas
            )
        except Exception as e:
            logger.exception(e)
            raise
        logger.info("self.collection.count {}".format(self.collection.count()))

        logger.info("Finished building knowledge!")
    def get_row(self, idx):
        # logger.info("self.search_df {}".format(self.search_df))

        if idx >= len(self.search_df) or idx < 0:
            falcon.HTTPBadRequest("snippets value not valid")

        return self.search_df.iloc[idx].to_dict()
    def get_text(self, idx):
        if idx >= len(self.search_df) or idx < 0:
            falcon.HTTPBadRequest("snippets value not valid")

        return self.search_df.iloc[idx]["article"]

    def need_emb(self):
        return True
    def get_name(self):
        return "語意搜尋"

    def search_uploaddata(self, sentence, **kwargs):
        uploaddata = kwargs["uploaddata"] # dict
        query_emb = kwargs["q_emb"] # list

        self.uploaddata_df = pd.DataFrame(uploaddata)
        self.uploaddata_df.to_csv('uploadfile.csv', encoding="utf-8-sig")
        ids, docs, embs, metas = self.get_collecttion_data(self.uploaddata_df, True)
        self.search_df = copy.deepcopy(self.uploaddata_df)


        # docs = [i for i in self.uploaddata_df["article"]]
      
        # ids= self.uploaddata_df["id"].values
        # ids = [str(i) for i in ids]
    
        # embs = [i for i in self.uploaddata_df["article_emb"].values]
        # logger.info("embs{}".format(type(self.uploaddata_df["article_emb"].values)))
        # logger.info("embs{}".format(type(self.uploaddata_df["article_emb"].values[0])))
        # logger.info("embs{}".format(type(self.uploaddata_df["article_emb"].values[0])))


        new_db_client = chromadb.Client()
        VECTOR_DB_NAME = 'uploaded_db'
        DIST_TYPE = "cosine"
        try:
            new_db_client.delete_collection(VECTOR_DB_NAME)
        except:
            pass
        self.new_collection = new_db_client.create_collection(
            VECTOR_DB_NAME,
            {
                "hnsw:space": DIST_TYPE,
                "hnsw:construction_ef": 100,
                "hnsw:M": 32
            }
        )         
        # try:
        self.new_collection.add(

            ids=ids,
            documents=docs,
            embeddings=embs,
            metadatas=metas
        )

        # except Exception as e:
        #     logger.exception(e)
        #     raise
        logger.info("after merge db {}".format(self.new_collection.count()))

        logger.info("Finished building knowledge!")
        results = self.new_collection.query(
            query_embeddings=query_emb,
            n_results=10,
        )
       
        ids = results["ids"][0]
        dists = results["distances"][0]

        outputs = []
        # if (file_by == []) & (filter_by is None) & (institution_by is None):
        #     return outputs
        for i in range(len(ids)):
            # if dists[i] >= DIST_THRESHOLD:
            #     break
            idx = int(ids[i])
            row = self.uploaddata_df.iloc[idx]
            # logger.info("meta {}".format(row["meta"]))
            # logger.info("meta {}".format(type(row["meta"])))
     
            r = SearchResult(
                index=idx,
                filename=row["file_name"],
                text=row["article"],
                query=sentence,
                # source=row["number"],
                source=row["source"],
                meta=row["meta"],

                # meta=str({'label':row["id"]}),
                # page=row["page"],
                dist=dists[i],
            )
            logger.info("r {}".format(r))

            outputs.append(r)

        logger.info("delete merge db {}".format(self.new_collection.count()))
        new_db_client.delete_collection(name=VECTOR_DB_NAME)
        # logger.info("delete  collection merge db {}".format(self.new_collection.count()))
        return outputs

    def get_collecttion_data(self, data, is_upload_data, model_name):
        import ast
        ids = [str(i) for i in range(data.shape[0])]
        # embs = [ast.literal_eval(i) for i in data["article_emb"]]
        if model_name == "gpt-4o":
          embs = [ast.literal_eval(str(i)) for i in data["gpt_context_emb"].values]
        else:
          embs = [ast.literal_eval(str(i)) for i in data["bge_context_emb"].values]
        
        logger.info(f"model_name: {model_name}")
        

        docs = data["article"].tolist()

        metas=[]
        for i, value in enumerate( data["meta"]):
            meta_dict = ast.literal_eval(str(value))
            meta_dict['is_upload_data'] = is_upload_data
            meta_dict['file_name'] = self.df.iloc[i]["file_name"]

            metas.append(meta_dict)
       
        return ids, docs, embs, metas
    
    
    def find_filename(self, query, db_filename):
    
        db_filenames = sorted(db_filename, key=len, reverse=True)
        match_filenames = []
        query_match_filenames=[]
        logger.info(f"query:{query}")

        for db_filename in db_filenames:
            if re.findall(db_filename,query):
                logger.info(f"db_filename: {db_filename}")
            
                query_match_filenames.append(db_filename)
        
        for db_filename in db_filenames:
            for query_match_filename in query_match_filenames:
                if re.findall(query_match_filename,db_filename):
                    match_filenames.append(db_filename)
        return match_filenames

      
    def search_files(self, sentence,model_name, **kwargs):
        label_by = kwargs["label_by"] # list
        file_by = kwargs["file_by"] # list
        uploaddata = kwargs["uploaddata"] # dict
        query_emb = kwargs["q_emb"] # list


        if model_name == "gpt":
          self.DIST_THRESHOLD=0.57

        else:
          self.DIST_THRESHOLD=0.41


        self.uploaddata_df = pd.DataFrame(uploaddata)
        self.uploaddata_df.to_csv('uploadfile.csv', encoding="utf-8-sig")
        self.df_merge = pd.concat([self.df,self.uploaddata_df])

        self.df_merge.reset_index()
        self.search_df = copy.deepcopy(self.df_merge)

        ids = [str(i) for i in range(self.df_merge.shape[0])][-self.uploaddata_df.shape[0]:]

        embs = [ast.literal_eval(str(i)) for i in self.uploaddata_df["article_emb"].values]
        docs = self.uploaddata_df["article"].tolist()
        # self.uploaddata_df["is_upload_data"]=True
        metas=[]
        for i in self.uploaddata_df["meta"]:
            meta_dict = ast.literal_eval(str(i))
            meta_dict['is_upload_data']=True
            meta_dict['file_name'] = self.uploaddata_df["file_name"].values[0]

            metas.append(meta_dict)

        VECTOR_DB_NAME = "pycon_law_rag"
        DIST_TYPE = "cosine"
        # self.db_client.reset()
        self.new_collection = self.db_client.get_collection(VECTOR_DB_NAME ,          
        {
                "hnsw:space": DIST_TYPE,
                # "hnsw:construction_ef": 50,
                # "hnsw:M": 16
                 "hnsw:construction_ef": 128,
                "hnsw:search_ef": 128,
                "hnsw:M": 128,
            })
 
        logger.info("before merge db {}".format(self.new_collection.count()))

        self.new_collection.add(
            ids=ids,
            documents=docs,
            embeddings=embs,
            metadatas=metas
        )
        logger.info("add new_collection {}".format(self.new_collection.count()))
      
        db_filename =  sorted(DB_FILENAME, key=len, reverse=True)
        match_filenames = self.find_filename(sentence,db_filename )
        data={}
        query_condition=[]
        for match_filename in match_filenames:
            data={}
            data['file_name']=match_filename
            query_condition.append(data)
        logger.info("query_condition {}".format(query_condition))
        
        if match_filenames:
          results = self.collection.query(query_emb,
        #    where={"file_name": match_filenames[0]},
           where={"$or": query_condition},

           n_results=10,
          )
        else:
          results = self.collection.query(
              query_embeddings=query_emb,
              n_results=10,
          )
        outputs = []
        # if (file_by == []) & (filter_by is None) & (institution_by is None):
        #     return outputs
     
        # logger.info(f"results: {results}")

        
        results_ids = results["ids"][0]
        dists = results["distances"][0]
        logger.info(f"result ids: {ids}")

        for i in range(len(results_ids)):
            # if dists[i] >= DIST_THRESHOLD:
            #     break
            idx = int(results_ids[i])
            row = self.df_merge.iloc[idx]
         
            df_label = ast.literal_eval(str(row["meta"]))["label"] 
            meta = ast.literal_eval(str(row["meta"]))
            meta['title'] = row['title']

            if not row["is_upload_data"]:
                if file_by :
                    if row["file_name"] not in file_by:
                        logger.info(f"not in file_b:")

                        continue
                else:
                    if label_by:
                        if df_label not in label_by:
                            logger.info(f"df_label not in label_by")
                            continue

            full_title_text = row["article"]
            full_title_text = ''.join(self.search_df.loc[(self.search_df["file_name"] == row["file_name"])&(self.search_df["title"] == row["title"]),"article"].values)

            r = SearchResult(
                index=idx,
                filename=row["file_name"],
                text=row["article"],
                query=sentence,
                source=row["number"],
                meta=meta,
                # page=row["page"],
                full_title_text = full_title_text,

                dist=dists[i],
            )
            outputs.append(r)
        self.new_collection.delete(
            ids=ids,
        )
        logger.info("delect add  collection  {}".format(self.new_collection.count()))
        return outputs

    def search(self, sentence ,model_name, **kwargs) -> List[SearchResult]:

        label_by = kwargs["label_by"] # list
        file_by = kwargs["file_by"] # list
        query_emb = kwargs["q_emb"] # list

        if model_name == "gpt-4o":
          self.DIST_THRESHOLD=0.57

        else:
          self.DIST_THRESHOLD=0.41
        logger.info(f"model_name: {model_name}")

        logger.info(f"DIST_THRESHOLD: {self.DIST_THRESHOLD}")

        db_filename =  sorted(DB_FILENAME, key=len, reverse=True)
        match_filenames = self.find_filename(sentence,db_filename )
        # collection.get(where={"$or": [{"author": "john"}, {"author": "jack"}]})
        logger.info(f"match_filenames: {match_filenames}")
        data={}
        query_condition=[]
        for match_filename in match_filenames:
            data={}
            data['file_name']=match_filename
            query_condition.append(data)
        logger.info("query_condition {}".format(query_condition))
        
        if match_filenames:
          results = self.collection.query(query_emb,
           where={"$or": query_condition},

           n_results=10,
          )
        else:
          results = self.collection.query(
              query_embeddings=query_emb,
              n_results=10,
          )
        self.search_df = copy.deepcopy(self.df)

        
        ids = results["ids"][0]
        dists = results["distances"][0]

        outputs = []
        # if (file_by == []) & (filter_by is None) & (institution_by is None):
        #     return outputs
        from collections import defaultdict
        uni_result = defaultdict(list)
        for i in range(len(ids)):
            if dists[i] >= self.DIST_THRESHOLD:
                break
            idx = int(ids[i])
            row = self.df.iloc[idx]
            # meta = row["meta"]
            if row["file_name"] in uni_result.keys():
              if row["title"] not in uni_result[row["file_name"]]:
                  uni_result[row["file_name"]].append(row["title"])
              else:
                continue
            else:
              uni_result[row["file_name"]].append(row["title"])
            meta = ast.literal_eval(row["meta"])
            meta['title'] = row['title']
            full_title_text = ''.join(self.df.loc[(self.df["file_name"] == row["file_name"])&(self.df["title"] == row["title"]),"article"].values)
            df_label = ast.literal_eval(row["meta"])["label"] 
          

            if file_by :
                if row["file_name"] not in file_by:
                    logger.info(f"not in file_b:")

                    continue
            else:
                if label_by:
                    if df_label not in label_by:
                        logger.info(f"df_label not in label_by")

                        continue
            r = SearchResult(
                index=idx,
                filename=row["file_name"],
                text=row["article"],
                query=sentence,
                source=row["number"],
                meta=meta,
                full_text='',
                full_title_text = full_title_text,
                dist=dists[i],
            )
            outputs.append(r)
        return outputs



