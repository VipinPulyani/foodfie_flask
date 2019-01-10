import requests
from datetime import date, timedelta
from flask import Blueprint
from flask import request
from flask_cors import CORS, cross_origin

import pymysql

import config

traSMS_api = Blueprint('traSMS_api', __name__)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


@traSMS_api.route("/api/v1.0/sendtraSMS", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def TransactionSMS():

    InitialURL = config.url
    Type = 'sendhttp.php?'
    AuthKey = config.authkey
    Sender = config.sender
    MobileNo = request.args.get('mobile')
    Message = request.args.get('message')

    url = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobiles=' + str(MobileNo) + '&message= '+ str(Message) + str(config.message) +'&sender='+ str(Sender) + '&route=4' + '&country=91'
    output = requests.get(url)
    return output.text, Message


def walletSMS(custonerId, amount, Balance):

    InitialURL = config.url
    Type = 'sendhttp.php?'
    AuthKey = config.authkey
    Sender = config.sender

    con, cur = connectDB()
    cur.execute('select CustomerPhoneNo from Customer where CustomerId= {0}'.format(str(custonerId)))
    MobileNo = cur.fetchall()[0][0]
    expire = date.today() + timedelta(days = 30)
    Message = 'Dear Guest, Your foodfie wallet has been credited with reload of INR {0}. Balance: INR {1}. Please redeem it before {2} else it will expired.'.format(amount, Balance, expire)

    url = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobiles=' + str(MobileNo) + '&message= '+ str(Message)  +'&sender='+ str(Sender) + '&route=4' + '&country=91'

    output = requests.get(url)
    return output.text, Message
