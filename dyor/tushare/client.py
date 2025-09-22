from functools import partial
from typing import Dict, List, Optional, Union
from dyor.http.request import HttpClient

class TushareClient(HttpClient):

    def __init__(self, token: str, base_url: str = "", headers: Dict | None = None):
        super().__init__(base_url, headers)
        self._token = token
    
    def _post(self, path: str, api_name: str, fields: List[str] = None, params: Optional[Dict] = None):
        """
        returns:
            fields: List[str]
            items: List[Dict]
        """
        d = {"api_name": api_name, "token": self._token, "params": params or {}}
        if fields:
            d["fields"] = ",".join(fields)
        response = self.post(path=path, data=d)
        response.raise_for_status()
        result = response.json()
        if result["code"] != 0:
            raise Exception(result["msg"])
        return result["data"]
    
    def __getattr__(self, name: str):
        return partial(self._post, "", name)

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        raise ValueError("TUSHARE_TOKEN environment variable not found")
        
    client = TushareClient(token=token, base_url="http://api.tushare.pro")
    params = {
        "ts_code": "600519.SH",
        "trade_date": "20241219"
    }
    print(client.daily(params=params))

    # params = {
    #     "ts_code": "600519.SH",
    # }
    # fields=[
    #     "ts_code",
    #     "symbol",
    #     "name",
    #     "area",
    #     "industry",
    #     "cnspell",
    #     "market",
    #     "list_date",
    #     "act_name",
    #     "act_ent_type",
    # ]
    # print(client.stock_basic(params=params, fields=fields))