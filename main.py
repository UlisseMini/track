import os
import time

import dominate.tags as t
import dotenv
from fastapi import FastAPI, Form, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
import jwt
dotenv.load_dotenv()


SECRET = os.environ['SECRET']


app = FastAPI()

ALGORITHM = 'HS256'


def auth(request: Request):
    if token := request.cookies.get('token'):
        data = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        if data['expires'] < time.time():
            raise HTTPException(status_code=403, detail='token expired')
        return data
    else:
        raise HTTPException(status_code=403, detail='token cookie not found')


@app.post('/login')
def login_post(password: str = Form(...)):
    response = RedirectResponse('/', status_code=303)
    if password == 'foo':
        expires = int(time.time()) + 60*60*24
        token = jwt.encode({'expires': expires}, SECRET, algorithm=ALGORITHM)
        response.set_cookie(key='token', value=token)

    return response


@app.get('/login')
def login_get():
    return HTMLResponse(t.html(
        t.head(t.title('track')),
        t.body(
            t.h1('hello'),
            t.form(
                t.input_(type='password', name='password'),
                t.br(),
                t.input_(type='submit', value='Login'),
                action='/login', method='POST'
            ),
        ),
    ).render())



habits = [
    ('Morning Exercise',),
    ('Anki reviews',),
    ('No time wasting till after 5pm',),
]

@app.get('/')
def index(jwt_data = Depends(auth)):


    return HTMLResponse()


