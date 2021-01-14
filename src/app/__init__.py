from flask import Flask
from src.config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "8v!3mj>bvtu95d50nw(-j3"


from src.app import routes
