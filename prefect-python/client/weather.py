# A simple example to demonstrate Prefect is working as expected
# Works with a local folder shared with the agents (/root/.prefect/flows by default).

import json
import requests
import prefect
from prefect import Flow, task, Client
from prefect.storage import Local

logger = prefect.context.get("logger")


@task
def get_woeid(city: str):
    logger.info("Getting {}'s woeid".format(city))
    api_endpoint = "https://www.metaweather.com/api/location/search/?query={}".format(
        city
    )
    response = requests.get(api_endpoint)
    if response.status_code == 200 or response.status_code == 401:
        payload = json.loads(response.text)
        return ""
    else:
        pass
        #raise ("Failed to query " + api_endpoint)


@task
def get_weather(woeid: int):
    logger.info("Getting weather of {}".format(woeid))
    api_endpoint = "https://api.openweathermap.org/data/2.5/weather?lat=48.8566&lon=2.3522&appid=c15b884d2459605438ddb909ee25ea6d"
    response = requests.get(api_endpoint)
    if response.status_code == 200 or response.status_code == 401:
        weather_data = json.loads(response.text)
        logger.debug(weather_data)
        return weather_data
    else:
        pass
        #raise ("Failed to query " + api_endpoint)


with Flow("Get Paris' weather", storage=Local(add_default_labels=False)) as flow:
    woeid = get_woeid("Paris")
    weather_data = get_weather(woeid)

try:
    client = Client()
    client.create_project(project_name="weather")
except prefect.utilities.exceptions.ClientError as e:
    logger.info("Project already exists")

flow.register(project_name="weather", labels=["development"], add_default_labels=False)

# Optionally run the code now
flow.run()
