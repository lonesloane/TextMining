#!/usr/bin/python2.7
import os
from rest import app as rest_api

if __name__ == '__main__':
    rest_api.app.run(debug=False, port=int(os.environ.get("PORT", 3000)))
