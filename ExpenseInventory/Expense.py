from collections import OrderedDict
from flask import Blueprint, render_template
from flask import request,jsonify
from flask_cors import CORS, cross_origin

import pymysql

import config
expense_api = Blueprint('expense_api', __name__)
CORS(expense_api)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


def getRawCategory(categoryId = 'Null'):

    conn, cur = connectDB()
    cur.execute("""select InventoryCategoryName 
                   from foodfie.InventoryCategoryRaw
                   where InventoryCategoryId=IFNULL({},InventoryCategoryId)""".format(categoryId))
    rawCategory = cur.fetchall()
    l_rawCategory = [cat[0] for cat in rawCategory]
    return l_rawCategory


def getMonthlyExpense():

    conn, cur = connectDB()
    cur.execute("""select MonthlyExpenseName 
                   from foodfie.MonthlyExpense""")
    rawCategory = cur.fetchall()
    l_rawCategory = [cat[0] for cat in rawCategory]
    return l_rawCategory


def getRawItems(itemId):

    conn, cur = connectDB()
    cur.execute('select InventoryItemName from foodfie.InventoryItemsRaw where InventoryCategoryId={}'.format(itemId))
    rawItem = cur.fetchall()
    l_rawItem = [cat[0] for cat in rawItem]
    return l_rawItem


@expense_api.route("/expense", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def expense():
    rawCategory = getRawCategory()
    return render_template('Expense.html')


@expense_api.route("/dailyexpense", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def dailyexpense():
    rawCategory = getRawCategory()
    return render_template('Category.html', rawCategory = rawCategory, categoryName = 'Daily Expense')


@expense_api.route("/monthlyexpense", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def monthlyexpense():
    rawItem = getMonthlyExpense()
    return render_template('MonthlyExpense.html', rawItem = rawItem, categoryName = 'Monthly Expense')


@expense_api.route("/Vegetables", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def vegetables():
    rawItem = getRawItems(1)
    commodityName = getRawCategory(1)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Chicken", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def chicken():
    rawItem = getRawItems(2)
    commodityName = getRawCategory(2)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Dairy", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def dairy():
    rawItem = getRawItems(3)
    commodityName = getRawCategory(3)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/GeneralStore", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def GeneralStore():
    rawItem = getRawItems(4)
    commodityName = getRawCategory(4)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Disposable", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Disposable():
    rawItem = getRawItems(5)
    commodityName = getRawCategory(5)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Fuel", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Fuel():
    rawItem = getRawItems(6)
    commodityName = getRawCategory(6)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Cleaning", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Cleaning():
    rawItem = getRawItems(7)
    commodityName = getRawCategory(7)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Misc", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Misc():
    rawItem = getRawItems(8)
    commodityName = getRawCategory(8)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/Roomali", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Roomali():
    rawItem = getRawItems(9)
    commodityName = getRawCategory(9)[0]
    return render_template('Commodity.html', rawItem = rawItem, commodityName = commodityName )


@expense_api.route("/submitExpense", methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def result():

    if request.method == 'POST':
        result = request.form.to_dict()
        finalResult = OrderedDict()
        for key, value in result.items():
            if 'QTY' in key:
                key = key.replace('QTY', '').strip()
                if not value == '':
                    finalResult[key] = [value]
        for key, value in result.items():
            if 'Amount' in key:
                key = key.replace('Amount', '').strip()
                if key in finalResult:
                    finalResult[key].append(value)

        for key, value in finalResult.items():
            conn, curs = connectDB()
            curs.execute("""Select InventoryCategoryId , InventoryItemId
                            from foodfie.InventoryItemsRaw
                            where InventoryItemName = '{}'""".format(key))
            inventoryDetail = curs .fetchall()
            perItem = float(value[1])/float(value[0])
            curs.execute("""insert into foodfie.DailyExpense 
                            ( InventoryCategoryId, InventoryItemId, QTY, PerPrice, TotalAmount) 
                            values({0}, {1}, {2}, {3}, {4})""".format(inventoryDetail[0][0], inventoryDetail[0][1], value[0],perItem ,value[1]))
            curs.execute('commit')

    return render_template("Thanks.html")


@expense_api.route("/submitMonthlyExpense", methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def result1():

     if request.method == 'POST':
        result = request.form.to_dict()
        finalResult = OrderedDict()
        for key, value in result.items():
            if 'Amount' in key:
                key = key.replace('Amount', '').strip()
                if not value == '':
                    finalResult[key] = value

        for key, value in finalResult.items():
            conn, curs = connectDB()
            curs.execute("""Select MonthlyExpenseId
                            from foodfie.MonthlyExpense
                            where MonthlyExpenseName = '{}'""".format(key))
            inventoryDetail = curs.fetchall()
            curs.execute("""insert into foodfie.MonthlyExpenseDetail 
                            (MonthlyExpenseId, MonthlyExpenseAmount) 
                            values({0}, {1})""".format(inventoryDetail[0][0], value))
            curs.execute('commit')

        return render_template("Thanks.html")
