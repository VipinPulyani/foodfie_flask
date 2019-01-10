import requests
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, Response
from random import randint
import config
PAY_API = Blueprint('pay_api', __name__)
CORS(PAY_API)

@PAY_API.route('/api/v1.0/payment', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Payment():
    resp = Response("")
    resp.headers['authorization'] =' Yet2l0scDaDYZw12patZT2QANsZgpUWBYcD6mAiuMDc='
    resp.headers['Content-Type'] = 'application/json'
    url = 'https://www.payumoney.com/payment/payment/smsInvoice?customerName=suryansh&customerMobileNumber=9711225007&description=toy&amount=500'
    output = requests.post(url)
    print(output)
    print(resp)

