import requests
import json
import time
from prometheus_client import start_http_server, Gauge

def get_iis_location(iss_location_url: str):
    """
    Get the current latitude and longitude of ISS.
    curl -GET http://api.open-notify.org/iss-now.json | jq .
    """
    try:
        response = requests.get(iss_location_url)
        data = response.json()
        print(data)
        return data
    except Exception as error:
        print('Error on get ISS location')
        raise error

def get_peoples_on_space(astros_on_space_url: str):
    """
    Get the number of people on space
    curl -GET curl -GET http://api.open-notify.org/astros.json | jq .
    """
    try:
        response = requests.get(astros_on_space_url)
        data = response.json()
        print(data)
        return data['number']
    except Exception as error:
        print('Error on get astros.')
        raise error
    
def update_metrics(astros_on_space_url: str, iss_location_url: str):
    """
    Update the number of peoples on space metric
    """ 
    try:
        number_of_peoples_on_space = Gauge('astronauts_on_space', 'Number of astronauts on space')
        iss_location_latitude = Gauge('iss_location_latitude', 'Current latitide of ISS')
        iss_location_longitude = Gauge('iss_location_longitude', 'Current longitude of ISS')
        while True:
            number_of_peoples_on_space.set(get_peoples_on_space(astros_on_space_url))
            iss_location_latitude.set(get_iis_location(iss_location_url)['iss_position']['latitude'])
            iss_location_longitude.set(get_iis_location(iss_location_url)['iss_position']['longitude'])
            #print(f'Number of people/astros on space in this moment: {number_of_people_on_space}.')
            time.sleep(300)
    except Exception as error:
        print('Error on update metric.')
        raise error

    
def exporter_http_server_init():
    """
    Init Prometheus http server
    """ 
    try:
        start_http_server(8899)
        print('HTTP Server initialited on port 8899')
        return True
    except Exception as error:
        print('Error on export http endpoint metrics')
        raise error
    
def main():
    """
    docker build -t gmaas2/poe:1.0
    docker run -d -p 8899:8899 --name poe-exporter gmaas2/poe:1.0
    """
    ASTROS_ON_SPACE_URL = 'http://api.open-notify.org/astros.json'
    ISS_LOCATION_URL = 'http://api.open-notify.org/iss-now.json'
    exporter_http_server_init()
    update_metrics(ASTROS_ON_SPACE_URL, ISS_LOCATION_URL)

if __name__ == '__main__':
    main()