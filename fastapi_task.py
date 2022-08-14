from fastapi import FastAPI, Body, Cookie, Form
from fastapi.responses import Response


app = FastAPI()


def standardize_phone(raw_number: str) -> str:
    number = ''.join(filter(str.isdigit, raw_number))
    if (
            (len(number) == 11) and (number.startswith('7') or number.startswith('8')) or
            (len(number) == 10) and (number.startswith('9'))
    ):
        number = number[-10:]
        return '8 ({}{}{}) {}{}{}-{}{}-{}{}'.format(*list(number))
    return number


@app.get('/')
def process_index():
    return Response("""
Hi! 
This is a simple FastApi app for final tasks of the
"Basics of computer and web technologies with Python" course on stepik.org by Digitalize.
        """)


@app.post('/unify_phone_from_json')
def standardize_phone_json(json_doc: dict = Body()) -> Response:
    raw_number = json_doc['phone']
    response = standardize_phone(raw_number=raw_number)
    return Response(response)


@app.post('/unify_phone_from_form')
def standardize_phone_form(phone: str = Form()) -> Response:
    response = standardize_phone(raw_number=phone)
    return Response(response)


@app.post('/unify_phone_from_query')
def standardize_phone_form(phone: str) -> Response:
    response = standardize_phone(raw_number=phone)
    return Response(response)


@app.post('/unify_phone_from_cookies')
def standardize_phone_form(phone: str = Cookie(default=None)) -> Response:
    response = standardize_phone(raw_number=phone)
    return Response(response)
