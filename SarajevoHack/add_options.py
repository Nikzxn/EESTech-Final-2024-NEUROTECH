import requests
import json
# Home Assistant API
from homeassistant_api import Client
from datetime import datetime, timedelta
# Voice Assistant
import pyttsx3
from googletrans import Translator, LANGUAGES


def get_val():
    ha_ip_addr = '10.11.22.52'
    ha_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzMGY5NTZmYWQxMTM0YzJiYWVkMmNmMDgxMTk2NmUyNSIsImlhdCI6MTcxNzI0MzA0MywiZXhwIjoyMDMyNjAzMDQzfQ.IOfRnnqDmJ3bA3LYg_sTUGdWFs5djNIIsOPEvSn9ZiE'
    params = ['co2_ppm', 'atmospheric_pressure', 'light', 'relative_humidity', 'temperature']
    entities = []
    for param in params:
        entities.append(f'sensor.psoc6_micropython_sensornode_open_space_{param}')
    history_minutes = 5

    with Client(
            f'http://{ha_ip_addr}:8123/api',
            ha_access_token
    ) as client:

        ent_values = []
        # Get entity from id
        for entity_id in entities:

            entity = client.get_entity(entity_id=entity_id)

            # Get data from this entity id for last n minutes
            start = datetime.now() - timedelta(minutes=history_minutes)
            history = client.get_entity_histories(entities=[entity], start_timestamp=start)

            # Go through each entity of the returned history data and save it's state values (here: atmospheric
            # pressure) to a list

            for entry in history:
                values = [x.state for x in entry.states]
            for i in range(len(values)):
                if values[i] == 'unknown':
                    if i == 0:
                        values[i] = values[i + 1]
                    values[i] = values[i - 1]
            ent_values.append(values)
    return ent_values


def make_response(my_question):
    ent_values = get_val()
    prompt = "These are CO2 measurement values of the last 5 minutes in ppm: " + \
             ", ".join([str(v) for v in ent_values[0]]) + '. '\
             "These are atmospheric pressure values of the last 5 minutes in hPa: " + \
             ", ".join([str(v) for v in ent_values[1]]) + '. '\
             "These are light values of the last 5 minutes in lx: " + \
             ", ".join([str(v) for v in ent_values[2]]) + '. '\
             "These are relative humidity of the last 5 minutes in %: " + \
             ", ".join([str(v) for v in ent_values[3]]) + '. '\
             "These are temperature of the last 5 minutes in celsius: " + \
             ", ".join([str(v) for v in ent_values[4]]) + '. '\
             "My question: " + my_question + '.'

    rules = ('You are assistant in smart house who makes recommendations to ensure the comfort of the environment. '
             '//Your language is ENGLISH. The informations should be published in the following edition: '
             '"qualitative characteristics of parameters", "Answer the main question by parametres of environment"'
             'Each information source has its own line. The first lines are confirmed by the parameters and their qualitative characteristics '
             '(too small, normal or too high). For example: “Temperature: normal”, “Humidity: too high” (only one word). '
             'Further on the following lines are paragraphs with answer of main question. '
             'Make your answer short (under 2 sentences).')
    prompt = {
        "modelUri": "gpt://b1gm5vbr11a3mrqc5loc/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [

            {
                "role": "system",
                "text": rules
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-key AQVNxgepJfUE156M83wHWCIgtVSWf63kQFRFx_D1"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    parsed_data = json.loads(result)

    # Достаем текст ответа
    response_text = parsed_data['result']['alternatives'][0]['message']['text']
    split_text = response_text.split('\n')
    summary_text = split_text[-1]

    return summary_text


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate", 135)  # Скорость произношения
    engine.setProperty("volume", 1)  # Громкость (минимум 0, максимум 1)
    engine.setProperty("voice", 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')

    engine.say(text)
    engine.runAndWait()


# type_get - `time` minutes or `count` last values
def get_data(number=1):
    ha_ip_addr = '10.11.22.52'
    ha_access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzMGY5NTZmYWQxMTM0YzJiYWVkMmNmMDgxMTk2NmUyNSIsImlhdCI6MTcxNzI0MzA0MywiZXhwIjoyMDMyNjAzMDQzfQ.IOfRnnqDmJ3bA3LYg_sTUGdWFs5djNIIsOPEvSn9ZiE'
    params = ['co2_ppm', 'atmospheric_pressure', 'light', 'relative_humidity', 'temperature']
    entities = []
    for param in params:
        entities.append(f'sensor.psoc6_micropython_sensornode_open_space_{param}')

    with Client(
            f'http://{ha_ip_addr}:8123/api',
            ha_access_token
    ) as client:
        ent_values = []
        for entity_id in entities:

            # Get entity from id
            entity = client.get_entity(entity_id=entity_id)
            history = client.get_entity_histories(entities=[entity])

            values = []
            for entry in history:
                values = [x.state for x in entry.states]

            if len(values) >= number:
                ent_values.append(values[-number:])
    return ent_values