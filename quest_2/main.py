import asyncio
import aiohttp
import gspread

import re
import copy

from config import *


RESULT = {}

async def parce_citilink(session: aiohttp.ClientSession, json_data: dict, retries=5):
    for attempt in range(retries):
        try:
            async with session.post(
                "https://www.citilink.ru/graphql/",
                cookies=COOKIES,
                headers=HEADERS,
                json=json_data,
            ) as response:
                return await response.json()
        except Exception as _ex:
            print(f"[INFO] - Ошибка запроса ({attempt + 1}/{retries}): {_ex}")
            await asyncio.sleep(2)
    return None


async def sorted_result_data(product: dict):
    global RESULT
    product_id = product["id"]
    price = product["price"]["current"]
    brand_match = re.search(r"\b(AMD|Intel)\b", product["name"], re.IGNORECASE)
    brand = brand_match.group(1) if brand_match else "Unknown"

    RESULT[product_id] = {
        "brand": brand,
        "model": product["shortName"],
        "price": float(price) if price else None,
    }


async def post_gspread():
    global RESULT
    RESULT = dict(sorted(RESULT.items(), key=lambda item: item[1]["price"] or float("inf"), reverse=True))

    gc = gspread.service_account(filename='quest_2/cred.json')
    wks = gc.open(SPREADSHEET_NAME).sheet1
    headers = ["ID", "Brand", "Model", "Price"]
    wks.clear()
    wks.append_row(headers)
    sorted_data = [[key, value["brand"], value["model"], value["price"]] for key, value in RESULT.items()]
    wks.append_rows(sorted_data)


async def main():
    async with aiohttp.ClientSession() as session:
        page = 1
        json_data = copy.deepcopy(JSON_DATA)
        while True:
            result = await parce_citilink(session, json_data)
            if not result:
                break

            products = result["data"]["productsFilter"]["record"]['products']
            if not products:
                break

            await asyncio.gather(
                *[sorted_result_data(product) for product in products]
            )
            page += 1
            json_data["variables"]["subcategoryProductsFilterInput"]["pagination"][
                "page"
            ] += 1

        await post_gspread()


if __name__ == "__main__":
    asyncio.run(main())
