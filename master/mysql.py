# -*- coding: utf-8 -*-

import mysql.connector


mydb= mysql.connector.connect(host="locahost",user ="udit" ,passwd ="Goverdhan@60")
mycursor =mydb.cursor()
mycursor.execute("Create DATABASE mydatabase")