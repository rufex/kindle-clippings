from src.tools import *

def test_date_1():
    assert get_date("Añadido el miércoles, 12 de enero de 2022 19:34:55") == datetime.datetime(2022, 1, 12, 19, 34, 55)

def test_date_2():
    assert get_date("- text | text, 1 of January of 2019 23:13:08") == datetime.datetime(2019, 1, 1, 23, 13, 8)

def test_date_3():
    assert get_date("Añadido el sábado 25 de junio de 2011 01H43' GMT") == None
