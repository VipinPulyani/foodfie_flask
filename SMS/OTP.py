import requests
import config
import urllib
from flask_cors import CORS, cross_origin
from flask import Blueprint, request
from random import randint
OTP_API = Blueprint('otp_api', __name__)
CORS(OTP_API)


@OTP_API.route('/api/v1.0/sendotp', methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def SendOTP():
    Type = 'sendotp.php?'
    AuthKey = config.authkey
    Message = urllib.parse.quote(config.message)
    Sender = config.sender
    InitialURL = config.url
    MobileNo = request.args.get('mobile')
    OTP = randint(1000,9999)

    url = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobile=' + str(MobileNo) + '&message='+ str(Message) + str(OTP) +'&sender='+ str(Sender) +'&otp=' + str(OTP) +''
    output = requests.get(url)
    return output.text


@OTP_API.route('/api/v1.0/verifyotp', methods = ['GET'])
def VerifyOTP():
    Type = 'verifyRequestOTP.php?'
    AuthKey = config.authkey
    MobileNo = request.args.get('mobile')
    OTP = request.args.get('otp')
    InitialURL = config.url

    verifyURL = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobile=' +str(MobileNo) + '&otp='+str(OTP)
    output = requests.get(verifyURL)
    return output.text


@OTP_API.route('/api/v1.0/retryotp', methods = ['POST'])
def RetryOTP():
    Type = 'retryotp.php?'
    AuthKey = config.authkey
    MobileNo = request.args.get('mobile')
    RetryType = 'text'
    InitialURL = config.url

    retryURL = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobile=' +str(MobileNo) + '&retrytype='+str(RetryType) +''
    output = requests.get(retryURL)
    return output.text
