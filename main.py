import platform
import aiohttp
import asyncio
import datetime
import os
import json
import sys

async def exchange_rates(days_count):
    async with aiohttp.ClientSession() as session:
        today = datetime.date.today()
        date = today - datetime.timedelta(days=days_count)
        formatted_date = date.strftime("%d.%m.%Y")
        result = [{formatted_date: {}}]
        async with session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={formatted_date}') as response:
            all_exchange_rates_list = await response.json()
            for el in all_exchange_rates_list['exchangeRate']:
                if el['currency'] == 'EUR' or el['currency'] == 'USD':
                    result[0][formatted_date].update({
                        el['currency']: {
                            'sale': round(el['saleRate'], 1),
                            'purchase': round(el['purchaseRate'], 1)
                        }
                    })
        return result

async def json_save(data):
    fname = 'data.json'
    loads = list()
    try:
        with open('data.json', 'r') as fl:
            loads = json.load(fl)
    except:
        with open(fname, 'w') as fl:
            fl.write(json.dumps([data], indent=2))
    if loads != []:
        loads.append(data)
        with open(fname, 'w') as fl:
            fl.write(json.dumps(remove_duplicates(loads), indent=2))

async def json_read():
    with open('data.json', 'r') as fl:
        loads = json.load(fl)
    return loads

def remove_duplicates(data_list):
    unique_data = []
    for data in data_list:
        if data not in unique_data:
            unique_data.append(data)
    return unique_data

async def main():
    try:
        if int(sys.argv[1]) > 10:
            return "You have violated the 10 day limit."
        else:
            exchange_rates_data = await exchange_rates(int(sys.argv[1]))
            for el in exchange_rates_data:
                await json_save(el)
            data_from_file = await json_read()
            return data_from_file
    except:
        return "Invalid number of days. Please provide a valid integer."
        
if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)
