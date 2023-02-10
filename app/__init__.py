# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 11:08:27 2021

@author: nadee
"""

from flask import Flask
app= Flask(__name__)
from app import views

app.static_folder="static"