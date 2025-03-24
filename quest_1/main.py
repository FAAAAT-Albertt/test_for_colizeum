import aiohttp
import asyncio
import aiofiles
import json
import pandas as pd


async def get_weather_api_data(session: aiohttp.ClientSession, lat: float, lon: float):
    API_KEY = "88c0436474d8abac7d623c847490420d"
    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
    try:
        async with session.get(url=URL) as response:
            result = await response.json()
            return result
    except Exception as _ex:
        print(f"[INFO] - {_ex}")
        return None


async def get_news_api_data(session: aiohttp.ClientSession):
    API_KEY = "1d2fcab2b9c9499ca0e7242f6443266e"
    URL = f"https://newsapi.org/v2/everything?q=PC%20gaming&apiKey={API_KEY}"
    try:
        async with session.get(url=URL) as response:
            result = await response.json()
            return result
    except Exception as _ex:
        print(f"[INFO] - {_ex}")
        return None


async def get_random_user_api_data(session: aiohttp.ClientSession):
    API_KEY = "tv6hpBHIQmlf4MoYdPuVTg==joKP0WX1xr39u0oa"
    URL = "https://api.api-ninjas.com/v1/randomuser"
    headers = {
        "X-Api-Key": API_KEY
    }
    try:
        async with session.get(url=URL, headers=headers) as response:
            result = await response.json()
            return result
    except Exception as _ex:
        print(f"[INFO] - {_ex}")
        return None


async def fetch_json_data(path):
    async with aiofiles.open(path, mode="r", encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)


async def main():
    cities = await fetch_json_data('quest_1/cities_weather.json')
    async with aiohttp.ClientSession() as session:
        tasks = []
        tasks.extend([get_weather_api_data(session, c["latitude"], c["longitude"]) for c in cities])
        tasks.append(get_news_api_data(session))
        tasks.extend([get_random_user_api_data(session) for _ in range(10)])
        results = await asyncio.gather(*tasks)

        weather_data = []
        news_data = []
        users_data = []

        for result in results:
            if result and len(result) == 13:
                weather_data.append(result)
            elif result and len(result) == 3:
                news_data.append(result)
            elif result and len(result) == 6:
                users_data.append(result)

        weather_df = pd.DataFrame(weather_data)
        news_df = pd.DataFrame(news_data)
        users_df = pd.DataFrame(users_data)

        with pd.ExcelWriter('quest_1/output.xlsx', engine='openpyxl') as writer:
            weather_df.to_excel(writer, sheet_name='Weather Data', index=False)
            news_df.to_excel(writer, sheet_name='News Data', index=False)
            users_df.to_excel(writer, sheet_name='User Data', index=False)


if __name__ == '__main__':
    asyncio.run(main())
