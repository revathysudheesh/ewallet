from fastapi import FastAPI
from database import load_config
from fastapi_sqlalchemy import DBSessionMiddleware
import  json
from endpoint import router 
import uvicorn
app = FastAPI()

SQLALCHEMY_DATABASE_URL = load_config('config.json')

app.add_middleware(DBSessionMiddleware, db_url=SQLALCHEMY_DATABASE_URL)

with open('config.json', 'r') as config_file:
        config = json.load(config_file)
app_config = config.get('app', {})
host=app_config.get('host',None)
port=app_config.get('port',None)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host=host, port=port,reload=True)
