from decimal import Decimal
from random import randint

import requests

from . conversion_tables import celsius_conv_table, fahrenheit_conv_table


class Client:
    def __init__(self, host, port, try_public=False):
        """
        Because we're using Ray we need this class to act as our client
        Otherwise the tests won't work correctly
        This class is a requests get wrapper that supplies the
        necessary host ip as a prefix to ensure the API
        requests can be fulfilled.
        :param host: the public ip address of the host or localhost
        :param try_public: if True will try to replace host with its public ip
        """
        self.host = host
        self.port = port
        self.ip = "127.0.0.1"
        if try_public:
            try:
                public_ip = (
                    requests.get('https://api.ipify.org').content.decode('utf8')
                )
                if len(public_ip) > 1:
                    self.ip = public_ip
            except Exception as e:
                print(f"unable to fetch public ip: {e}")
            if self.host != self.ip:
                self.host = self.ip
        self.url_prefix = f"http://{self.host}:8080"

    def get(self, url_suffix):
        """
        :param url_suffix: url without hostname and port
        :return: response of requests using constructed url
        """
        return requests.get(f"{self.url_prefix}{url_suffix}")


# set client to local host
# replace it with the public ip if it's available
client = Client("127.0.0.1", port="8080", try_public=True)


def _choose_five_random_indices():
    seen_indices = set()
    seek_count = 0
    length_table = len(celsius_conv_table)
    max_seeks = 10000
    while seek_count < max_seeks and len(seen_indices) < 5:
        index = randint(0, length_table - 1)
        if index not in seen_indices:
            seen_indices.add(index)
        seek_count += 1
    return list(seen_indices)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Temperature Converter API",
        "endpoints": ["/convert"],
        "documentation": "/documentation",
        "open-api-doc": "/openapi.json"
    }


def test_read_convert():
    response = client.get("/convert")
    assert response.status_code == 200
    assert response.json() == {
        "message": "This endpoint is Used to convert temperatures",
        "documentation": "/documentation",
        "open-api-doc": "/openapi.json"
    }


random_indices = _choose_five_random_indices()


def _check_conversion_response(response, unit2):
    try:
        assert response.status_code == 200
        json_dict = response.json()
        assert len(json_dict) == 1
        # only use one decimal place to prevent
        # the less precise table to fail tests
        assert (
            round(Decimal(json_dict["value"]).quantize(Decimal('.01')), 1)
            == round(Decimal(unit2).quantize(Decimal('.01')), 1)
        )
    except AssertionError:
        return False
    return True


def test_celsius_exceeds_absolute_zero():
    response = client.get("/convert/-273.150001/celsius/fahrenheit")
    assert (response.status_code < 199) or (response.status_code > 299)
    assert response.json() == {
        "detail": "Values lower than absolute zero are not allowed"
    }


def test_fahrenheit_exceeds_absolute_zero():
    response = client.get("/convert/-459.670001/celsius/fahrenheit")
    assert (response.status_code < 199) or (response.status_code > 299)
    assert response.json() == {
        "detail": "Values lower than absolute zero are not allowed"
    }


def test_convert_invalid_unit():
    response = client.get("/convert/30/celsius/kelvin")
    assert (response.status_code < 199) or (response.status_code > 299)


def test_convert_invalid_temperature():
    response = client.get("/convert/forty/fahrenheit/celsius")
    assert (response.status_code < 199) or (response.status_code > 299)


def test_convert_extra_parameter():
    response = client.get("/convert/72/fahrenheit/celsius/precision")
    assert (response.status_code < 199) or (response.status_code > 299)


def test_celsius_to_fahrenheit_random_case_1():
    temp_unit1 = celsius_conv_table[random_indices[0]][0]
    temp_unit2 = celsius_conv_table[random_indices[0]][1]
    celsius_to_fahrenheit_url = f"/convert/{temp_unit1}/celsius/fahrenheit"
    response = client.get(celsius_to_fahrenheit_url)
    assert _check_conversion_response(response, temp_unit2)

def test_celsius_to_fahrenheit_random_case_2():
    index_2 = (
        random_indices[0] if 1 < len(random_indices) else random_indices[1]
    )
    temp_unit1 = celsius_conv_table[index_2][0]
    temp_unit2 = celsius_conv_table[index_2][1]
    celsius_to_fahrenheit_url = f"/convert/{temp_unit1}/celsius/fahrenheit"
    response = client.get(celsius_to_fahrenheit_url)
    assert _check_conversion_response(response, temp_unit2)


def test_celsius_to_fahrenheit_random_case_3():
    index_3 = (
        random_indices[0] if 2 < len(random_indices) else random_indices[2]
    )
    temp_unit1 = celsius_conv_table[index_3][0]
    temp_unit2 = celsius_conv_table[index_3][1]
    celsius_to_fahrenheit_url = f"/convert/{temp_unit1}/celsius/fahrenheit"
    response = client.get(celsius_to_fahrenheit_url)
    assert _check_conversion_response(response, temp_unit2)


def test_celsius_to_fahrenheit_random_case_4():
    index_4 = (
        random_indices[0] if 3 < len(random_indices) else random_indices[3]
    )
    temp_unit1 = celsius_conv_table[index_4][0]
    temp_unit2 = celsius_conv_table[index_4][1]
    celsius_to_fahrenheit_url = f"/convert/{temp_unit1}/celsius/fahrenheit"
    response = client.get(celsius_to_fahrenheit_url)
    assert _check_conversion_response(response, temp_unit2)


def test_celsius_to_fahrenheit_random_case_5():
    index_5 = (
        random_indices[0] if 4 < len(random_indices) else random_indices[4]
    )
    temp_unit1 = celsius_conv_table[index_5][0]
    temp_unit2 = celsius_conv_table[index_5][1]
    celsius_to_fahrenheit_url = f"/convert/{temp_unit1}/celsius/fahrenheit"
    response = client.get(celsius_to_fahrenheit_url)
    assert _check_conversion_response(response, temp_unit2)


def test_fahrenheit_to_celsius_random_case_2():
    index_2 = (
        random_indices[0] if 1 < len(random_indices) else random_indices[1]
    )
    temp_unit1 = fahrenheit_conv_table[index_2][0]
    temp_unit2 = fahrenheit_conv_table[index_2][1]
    fahrenheit_to_celsius_url = f"/convert/{temp_unit1}/fahrenheit/celsius/"
    response = client.get(fahrenheit_to_celsius_url)
    assert _check_conversion_response(response, temp_unit2)


def test_fahrenheit_to_celsius_random_case_3():
    index_3 = (
        random_indices[0] if 2 < len(random_indices) else random_indices[2]
    )
    temp_unit1 = fahrenheit_conv_table[index_3][0]
    temp_unit2 = fahrenheit_conv_table[index_3][1]
    fahrenheit_to_celsius_url = f"/convert/{temp_unit1}/fahrenheit/celsius/"
    response = client.get(fahrenheit_to_celsius_url)
    assert _check_conversion_response(response, temp_unit2)


def test_fahrenheit_to_celsius_random_case_4():
    index_4 = (
        random_indices[0] if 3 < len(random_indices) else random_indices[3]
    )
    temp_unit1 = fahrenheit_conv_table[index_4][0]
    temp_unit2 = fahrenheit_conv_table[index_4][1]
    fahrenheit_to_celsius_url = f"/convert/{temp_unit1}/fahrenheit/celsius/"
    response = client.get(fahrenheit_to_celsius_url)
    assert _check_conversion_response(response, temp_unit2)


def test_fahrenheit_to_celsius_random_case_5():
    index_5 = (
        random_indices[0] if 4 < len(random_indices) else random_indices[4]
    )
    temp_unit1 = fahrenheit_conv_table[index_5][0]
    temp_unit2 = fahrenheit_conv_table[index_5][1]
    fahrenheit_to_celsius_url = f"/convert/{temp_unit1}/fahrenheit/celsius/"
    response = client.get(fahrenheit_to_celsius_url)
    assert _check_conversion_response(response, temp_unit2)