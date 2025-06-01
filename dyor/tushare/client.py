from typing import Dict, Optional, Union
from dyor.http.request import HttpClient

class TushareClient(HttpClient):

    def __init__(self, token: str, base_url: str = "", headers: Dict | None = None):
        super().__init__(base_url, headers)
        self._token = token
    
    def _post(self, path: str, data: Optional[Dict] = None):
        d = {"token": self._token}
        if data:
            d.update(data)
        return self.post(path=path, data=d)
    
    def daily(self, params: Dict) -> Dict:
        data = {
            "api_name": "daily",
            "params": params,
        }
        response = self._post("", data=data)
        response.raise_for_status()
        return response.json()

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