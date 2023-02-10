# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 11:42:14 2021

@author: nadee
"""

from app import app

if __name__ == '__main__':
  app.run(debug = False,host='0.0.0.0', port=8000) #port = 8000