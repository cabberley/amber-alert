from datetime import datetime
from time import sleep as wait
import json
import os
import requests

# Get the current datetime
now = datetime.now()
# Load environment variables
try:
    siteId = os.environ["AMBER_SITE_ID"]
    apiKey = os.environ["AMBER_API_KEY"]
    homeAssistantUri = os.environ["HOME_ASSISTANT_URI"]
    homeAssistantBearer = os.environ["HOME_ASSISTANT_BEARER"]
    amberFeedInPriceSensor = os.environ["AMBER_FEED_IN_PRICE_SENSOR"]
    amberGeneralPriceSensor = os.environ["AMBER_GENERAL_PRICE_SENSOR"] #os.environ["AMBER_GENERAL_PRICE_SENSOR"]
    amberPriceDate = os.environ["AMBER_PRICE_DATE_SENSOR"]
    alertHigh = float(os.environ["ALERT_HIGH"])
    alertLow = float(os.environ["ALERT_LOW"])
    priceRes = os.environ["DATA_RES"]
    waitTime = int(os.environ["WAIT_TIME"])
except KeyError as e:
    raise Exception(f"Missing environment variable: {e}")
except ValueError as e:
    raise Exception(f"Invalid value for environment variable: {e}")

# For testing
#siteId = "01GA20DWHV68RDSR7220XWXW22" #os.environ["AMBER_SITE_ID"]
#apiKey = "psk_d1b9987ed49214958c792d630ad5a941" #os.environ["AMBER_API_KEY"]
#homeAssistantUri = "http://192.168.4.18:8123" #os.environ["HOME_ASSISTANT_URI"]
#homeAssistantBearer = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiZGFlYWE3YTY1ZjM0MTE0OGNkN2U5Yzc2OGRiMDIzYiIsImlhdCI6MTczNDA2MTE4NSwiZXhwIjoyMDQ5NDIxMTg1fQ.r667vNQ98z83Yp5_CA9J1xXD5gCill6Hq4vBs10aTZo" #os.environ["HOME_ASSISTANT_BEARER"]
#amberFeedInPriceSensor = "sensor.amber_electric_feed_in_price" #os.environ["AMBER_FEED_IN_PRICE_SENSOR"]
#amberGeneralPriceSensor = "sensor.amber_electric_general_price" #os.environ["AMBER_GENERAL_PRICE_SENSOR"] #os.environ["AMBER_GENERAL_PRICE_SENSOR"]
#amberPriceDate = "sensor.amber_electric_price_date" #os.environ["AMBER_PRICE_DATE_SENSOR"]
#alertHigh = 30 #float(os.environ["ALERT_HIGH"])
#alertLow = 10 #float(os.environ["ALERT_LOW"])
#priceRes = 5 #os.environ["DATA_RES"]
#waitTime = 2 #int(os.environ["WAIT_TIME"])

def getAmber(siteId, apiKey, priceRes, checkTime):
    # Set the URL for the Amber Electric API
    apiUrl = (
        f"https://api.amber.com.au/v1/sites/{siteId}/prices/current?resolution={priceRes}"
    )

    # Get current price data from the API and parse the JSON
    try:
        apiResponse = requests.get(
            apiUrl, headers={"accept": "application/json", "Authorization": f"Bearer {apiKey}"}, timeout=10
        )
        apiResponse.raise_for_status()
        priceDataApi = apiResponse.json()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"API request failed: {e}") from e

    return priceDataApi[1]["estimate"], priceDataApi #timeCheck

def updateHomeAssistant(homeAssistantUri, homeAssistantBearer, amberFeedInPriceSensor, amberGeneralPriceSensor, amberPriceDate, amberPriceData):
    # Set the headers for the API request
    headers = {
        "Authorization": f"Bearer {homeAssistantBearer}",
        "Content-Type": "application/json",
    }

    # Set the URL for the Home Assistant API
    apiUrl = f"{homeAssistantUri}/api/states/{amberGeneralPriceSensor}"

    currentPrice = float(amberPriceData[0]["perKwh"])
    currentPrice2 = "{:.2f}".format(currentPrice)
    
    data = {
        "state": currentPrice2,
        "attributes": {
            "unit_of_measurement": "c/kWh",
            "unique_id": "amber_electric_general_price",
            "friendly_name": "Amber Electric General Price",
            "start_time": amberPriceData[0]["startTime"],
            "end_time": amberPriceData[0]["endTime"],
            "nem_time": amberPriceData[0]["nemTime"],
            "estimate": amberPriceData[0]["estimate"],
        },
    }

    # Send the API request to update the sensor state
    try:
        response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e

    # Set the URL for the Home Assistant API
    apiUrl = f"{homeAssistantUri}/api/states/{amberFeedInPriceSensor}"

    currentPrice = float(amberPriceData[1]["perKwh"])
    currentPrice2 = "{:.2f}".format(currentPrice)
    
    data = {
        "state": currentPrice2,
        "attributes": {
            "unit_of_measurement": "c/kWh",
            "unique_id": "amber_electric_feed_in_price",
            "friendly_name": "Amber Electric Feed-in Price",
            "start_time": amberPriceData[1]["startTime"],
            "end_time": amberPriceData[1]["endTime"],
            "nem_time": amberPriceData[1]["nemTime"],
            "estimate": amberPriceData[1]["estimate"],
        },
    }

    # Send the API request to update the sensor state
    try:
        response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e

    # Set the URL for the Home Assistant API
    apiUrl = f"{homeAssistantUri}/api/states/{amberPriceDate}"

    dateConvert = (datetime.strptime(amberPriceData[1]["startTime"], "%Y-%m-%dT%H:%M:%S%z"))
    data = {
        "state": dateConvert.isoformat(),
        "attributes": {
            "unique_id": "amber_electric_price_date",
            "friendly_name": "Amber Electric Date Price",
        },
    }

    # Send the API request to update the sensor state
    try:
        response = requests.post(apiUrl, headers=headers, json=data, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Home Assistant API request failed: {e}") from e

timeLoop = True
#while timeLoop:
wait(1)
checkTime = datetime.now().strftime("%M")
if int(checkTime) % 5 == 0:
    estimatePrice=True
    while estimatePrice:
        estimatePrice, amberPriceData = getAmber(siteId, apiKey, priceRes,checkTime)
        print(estimatePrice)
        wait(waitTime)
    timeLoop = False
    updateHomeAssistant(homeAssistantUri, homeAssistantBearer, amberFeedInPriceSensor, amberGeneralPriceSensor, amberPriceDate, amberPriceData)
else:
    wait(5)
