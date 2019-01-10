from collections import OrderedDict
from flask import Blueprint, render_template
from flask import request,jsonify
from flask_cors import CORS, cross_origin

import pymysql

import config
sales_api = Blueprint('sales_api', __name__)
CORS(sales_api)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


@sales_api.route("/sales")
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def sales():
    return render_template('Sales.html', rawCategory ='test')


@sales_api.route("/submitSales", methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def submitsales():

    if request.method == 'POST':
        result = request.form.to_dict()
        conn, curs = connectDB()
        saleType = ",".join(item for item in result.keys())
        saleAmount = ",".join(item if item != '' else '0' for item in result.values())

        curs.execute("""insert into foodfie.DailySales
                        ({0}) 
                        values({1})""".format(saleType, saleAmount))

        curs.execute('commit')

    return render_template("Thanks.html")
