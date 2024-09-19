from dataclasses import dataclass, field
from typing import List


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
