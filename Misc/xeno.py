from collections import OrderedDict


import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint, request, Response, jsonify

import config

xeno_API = Blueprint('xeno_api', __name__)
CORS(xeno_API)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


@xeno_API.route('/api/bills', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def xeno():

    startDate = request.args.get('from')
    endDate = request.args.get('to')

    if startDate and endDate:
        conn, cur = connectDB()
        cur.execute(""" select a.OrderId, b.CustomerPhoneNo, a.TotalAmount, a.OrderTime
                        from foodfie.Order a
                        join foodfie.Customer b
                        on a.CustomerId = b.CustomerId
                        where OrderTime between '{0}' and '{1}'""".format(startDate, endDate))
        customerData = cur.fetchall()

        customerDetail = [dict((x,y) for x,y in zip(('OrderId', 'CustomerPhoneNo', 'TotalAmount', 'OrderTime'), row)) for row in customerData]

    return jsonify({'customer_data':customerDetail}) if (startDate and endDate) else jsonify({'customer_data': 'Please check Start Date(from=) or End Date(to=). Format:2017-12-18 00:00:00'})


