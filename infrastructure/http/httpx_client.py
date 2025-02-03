import httpx

from protocols.http_client import HTTPClient


class HttpxClient(HTTPClient):
    async def post(self, url, data=None, json=None, headers=None):
        print(json)
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, data=data, json=json, headers=headers)
            return response.json()

    async def get(self, url, params=None, headers=None):
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, params=params, headers=headers)
            return response.json()
