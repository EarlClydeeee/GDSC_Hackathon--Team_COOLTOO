# This file will be used to import all routes for the application.


from flask import Flask

app = Flask(__name__,
            static_folder='../statics',    
            template_folder='../templates')

from .index import *
from .incident import *  