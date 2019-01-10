import pymysql
import config
from collections import OrderedDict
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
from threading import Thread


from ExpenseInventory.Expense import expense_api
from ExpenseInventory.Inventory import inventory_api, updateLiveInventory
from Misc.PaymentGateway import PAY_API
from Order import OrdDet_API
from Recipes.Recipes import recipe_api
from SMS.OTP import OTP_API
from SMS.TransactionSMS import traSMS_api
from SMS.SMS_Misc import sendOrderSMS, sendSMS
from Wallet.Wallet import wallet_api, updateWalletAmount, redeemWalletBalance
from Misc.Sales import sales_api
from Misc import xeno
from CouponCode.Coupon import coupon_API, redeemcoupon
from MLM import foodfie_MLM

application = Flask(__name__)
CORS(application)
application.register_blueprint(OTP_API)
application.register_blueprint(coupon_API)
application.register_blueprint(traSMS_api)
application.register_blueprint(PAY_API)
application.register_blueprint(OrdDet_API)
application.register_blueprint(wallet_api)
application.register_blueprint(recipe_api)
application.register_blueprint(expense_api)
application.register_blueprint(inventory_api)
application.register_blueprint(sales_api)
application.register_blueprint(xeno.xeno_API)
# application.register_blueprint(OrdDet_API)
application.config["JSON_SORT_KEYS"] = False


@application.route('/')
def index():
    return "Foodfie API!"


@application.route("/all")
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def allPages():
    return render_template('index.html', test ='test')


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


@application.route('/api/v1.0/verifyemployee', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def VerifyEmploye():
    username = request.args.get('username')
    password = request.args.get('password')
    conn, cursor = connectDB()
    cursor.execute("""Select a.StoreId, b.StoreName, b.PackagingAmount, b.CashTaxPer
                      from foodfie.Employee a
                      join foodfie.Store b
                      on a.StoreId = b.StoreId 
                      where a.username ='{0}' and a.password = '{1}'""".format(username, password))
    data = cursor.fetchall()[0]
    if len(data) == 0:
        return jsonify({'StoreId': -1})
    else:
        return jsonify({'StoreId': data[0],
                        'StoreName': data[1],
                        'PackagingAmount':data[2],
                        'CashTax':data[3]
                       })


@application.route('/api/v1.0/verifycustomer', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def VerifyCustomer():
    mobileNo = request.args.get('mobileno')
    conn, cursor = connectDB()
    cursor.execute("""Select CustomerId, CustomerPhoneNo, CustomerName 
                      from foodfie.Customer where customerphoneno =""" + str(mobileNo))
    data = cursor.fetchall()
    return jsonify({'isExist': 1} if data else {'isExist': 0})


@application.route('/api/v1.0/verifymobile', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def VerifyMobileNo():
    mobileNo = request.args.get('mobileno')
    storeId = request.args.get('storeid')
    referenceCode = request.args.get('reference_code')
    conn, cursor = connectDB()
    cursor.execute("""Select CustomerId, CustomerPhoneNo, CustomerName 
                      from foodfie.Customer where customerphoneno =""" + str(mobileNo))
    data = cursor.fetchall()
    if len(data) == 0:
        referenceCode = None if referenceCode == '' else referenceCode
        cursor.execute("""insert into foodfie.Customer (CustomerPhoneNo,StoreId,RegisterDate, ReferredBy) 
                          values ('{0}',{1}, current_timestamp, '{2}')""".format(mobileNo, storeId, referenceCode))
        conn.commit()
        cursor.execute('select customerid, customername from foodfie.Customer order by 1 desc limit 1;')
        result = cursor.fetchall()
        return jsonify({'ID':result[0][0],'Name': result[0][1]})
    else:
        return jsonify({'ID':data[0][0],'Name': data[0][2]})


@application.route('/api/v1.0/newcustomer', methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def NewCustomer():
        CustomerMobileNo = request.args.get('mobile')
        CustomerName = request.args.get('name')
        conn, cursor = connectDB()
        cursor.execute('insert into foodfie.Customer (CustomerPhoneNo,CustomerName,RegisterDate) values ("' + str(CustomerMobileNo) + '","' + str(CustomerName) + '", current_timestamp);')
        conn.commit()
        cursor.execute('select customerid, customername from foodfie.Customer order by 1 desc limit 1;')
        data = cursor.fetchall()
        conn.close()
        if len(data) == 0:
            return jsonify({})
        else:
            return jsonify({'ID':data[0][0],'Name': data[0][1]})


@application.route('/api/v2.0/newcustomer', methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def NewCustomers():
        CustomerMobileNo = request.args.get('mobile')
        conn, cursor = connectDB()
        cursor.execute('insert into foodfie.Customer (CustomerPhoneNo,RegisterDate) values ("' + str(CustomerMobileNo) + '", current_timestamp);')
        conn.commit()
        cursor.execute('select customerid from foodfie.Customer order by 1 desc limit 1;')
        data = cursor.fetchall()
        conn.close()
        if len(data) == 0:
            return jsonify({})
        else:
            return jsonify({'ID':data})


@application.route('/api/v1.0/category', methods = ['GET','PUT','POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Category():
    if request.method == 'POST':
        CategoryName = request.args.get('categoryname')
        conn, cur = connectDB()
        cur.execute('insert into foodfie.Category (CategoryName) values("' +str(CategoryName) +'")')
        conn.commit()
        conn.close()
        return jsonify({'Result': 'Successful'})

    elif request.method == 'GET':
        output = {}
        conn, cur = connectDB()
        cur.execute('Select * from Category')
        result = cur.fetchall()
        for re in result:
            output[re[0]] = re[1]
        return jsonify({"Category" : output})

    elif request.method == 'PUT':
        pass

#
# @application.route('/api/v1.0/item', methods = ['GET'])
# @cross_origin(origin='*',headers=['Content- Type','Authorization'])
# def GetItem():
#     categoryId = request.args.get('categoryid')
#     if categoryId is not None:
#         conn, cursor = connectDB()
#         cursor.execute("Select ItemId,ItemName, Quantity, ItemPrice, CategoryId from foodfie.Item where categoryid=" + str(categoryId))
#         data = cursor.fetchall()
#         if len(data) == 0:
#             return jsonify({})
#         else:
#             items = OrderedDict()
#             for item in data:
#                 items[item[0]] = OrderedDict()
#                 for x,y in zip(('ID', 'Type', 'Qty', 'Price', 'CatagoryId'), item):
#                     items[item[0]][x] = y
#             return jsonify({'Item': items})
#     else:
#         conn, cursor = connectDB()
#         cursor.execute("Select ItemId, ItemName, Quantity, ItemPrice, CategoryId from foodfie.Item")
#         data = cursor.fetchall()
#         if len(data) == 0:
#             return jsonify({})
#         else:
#             items = OrderedDict()
#             for item in data:
#                 items[item[0]] = OrderedDict()
#                 for x,y in zip(('ID', 'Type', 'Qty', 'Price', 'CatagoryId'), item):
#                     items[item[0]][x] = y
#
#             return jsonify({'Item': items})


@application.route('/api/v2.0/item', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def NewGetItem():
    categoryId = request.args.get('categoryid')
    if categoryId is not None:

        conn, cursor = connectDB()
        cursor.execute("""select CategoryId, ItemName, ItemId, ItemPrice, Quantity
                          from foodfie.Item
                          where categoryid = %s
                          group by CategoryId, ItemName, Quantity
                          order by CategoryId, ItemId;""" %categoryId)
        data = list(cursor.fetchall())
        if len(data) == 0:
            return jsonify({})
        else:
            count = 1
            items = OrderedDict()
            while len(data) > 0:
                firstelement = data[0]
                itemlist = [item for item in data if item[0] == firstelement[0] and item[1] == firstelement[1]]
                run = 0
                items[count] = OrderedDict()
                for no, item in enumerate(itemlist):
                    if run < 1:
                        for x,y in zip(('CatagoryId', 'Type' ), (item[0], item[1])):
                            items[count][x] = y
                            run += 1
                        items[count]["items"] = OrderedDict()
                    items[count]["items"][no] = OrderedDict()
                    for x,y in zip(('ID', 'Price', 'Qty' ), (item[2], item[3], item[4])):
                        items[count]["items"][no][x] = y
                    data.remove(item)
                count +=1
            return jsonify({'Item': items})
    else:
        conn, cursor = connectDB()
        cursor.execute("""select CategoryId, ItemName, ItemId, ItemPrice, Quantity
                          from foodfie.Item
                          group by CategoryId, ItemName, Quantity
                          order by CategoryId, ItemId;""")
        data = list(cursor.fetchall())
        if len(data) == 0:
            return jsonify({})
        else:
            count = 1
            items = OrderedDict()
            while len(data) > 0:
                firstelement = data[0]
                itemlist = [item for item in data if item[0] == firstelement[0] and item[1] == firstelement[1]]
                run = 0
                items[count] = OrderedDict()
                for no, item in enumerate(itemlist):
                    if run < 1:
                        for x,y in zip(('CatagoryId', 'Type' ), (item[0], item[1])):
                            items[count][x] = y
                            run += 1
                        items[count]["items"] = OrderedDict()
                    items[count]["items"][no] = OrderedDict()
                    for x,y in zip(('ID', 'Price', 'Qty' ), (item[2], item[3], item[4])):
                        items[count]["items"][no][x] = y
                    data.remove(item)
                count +=1

            return jsonify({'Item': items})


@application.route('/api/v4.0/order', methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def Orderss():
    try:
        CustomerId = request.args.get('customerid')
        storeId = request.args.get('storeid')
        TotalAmount = request.args.get('totalamount')
        PaymentType = request.args.get('paymenttype')
        ItemId = request.args.get('itemid') if request.args.get('itemid') is None else request.args.get('itemid').split(',')
        QTY = request.args.get('qty') if request.args.get('qty') is None else request.args.get('qty').split(',')
        Price = request.args.get('price') if request.args.get('price') is None else request.args.get('price').split(',')
        IsRedeem = request.args.get('isredeem')
        NetAmount = request.args.get('netamount')
        OrderType = request.args.get('ordertype')
    except:
        return jsonify({'Variable Not Set': 'Unsuccessful'})

    try:
        conn, cursor = connectDB()

        cursor.execute("""insert into foodfie.Order(CustomerId,StoreId,TotalAmount,PaymentType,NetAmount, Order_Type) values ({0}, {1}, {2},'{3}', {4}, '{5}')""".format(str(CustomerId), str(storeId), str(TotalAmount), str(PaymentType), str(NetAmount), str(OrderType)))
        conn.commit()

        # Find the Order Id from the Order Table
        cursor.execute('Select OrderId from foodfie.Order order by OrderId desc limit 1 ;')
        OrderId = cursor.fetchone()[0]

        # Wallet Functionality
        if IsRedeem == 'true':
            TotalAmount = int(TotalAmount)
            redeemWalletBalance(OrderId, CustomerId, TotalAmount)


        # Wallet Functionality
        updateWalletAmount(CustomerId, NetAmount, OrderId)

        # Verify no rows are already present in OrderDetail table
        cursor.execute('Select * from foodfie.OrderDetail where OrderId=' + str(OrderId))
        OrderIdExist = cursor.fetchall()
        if OrderIdExist.__len__() == 0:
            for Item, Qt, Pri in zip(ItemId,QTY,Price):
                cursor.execute('insert into foodfie.OrderDetail (OrderId,ItemId,QTY,Price) values (' + str(OrderId) + ',' + str(Item) + ',"' +str(Qt) + '", '+ str(Pri) +');')
                conn.commit()
            return jsonify({'OrderId': OrderId})
        else:
            return jsonify({'Something Weired in Order': 'UnSuccessful'})
    except:
        return jsonify({'Data Issue': 'UnSuccessful'})
    finally:
        conn.commit()
        conn.close()


@application.route('/api/v3.0/order', methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def orders():
    try:
        CustomerId = request.args.get('customerid')
        storeId = request.args.get('storeid')
        TotalAmount = request.args.get('totalamount')
        PaymentType = request.args.get('paymenttype')
        ItemId = request.args.get('itemid') if request.args.get('itemid') is None else request.args.get('itemid').split(',')
        QTY = request.args.get('qty') if request.args.get('qty') is None else request.args.get('qty').split(',')
        Price = request.args.get('price') if request.args.get('price') is None else request.args.get('price').split(',')
        IsRedeem = request.args.get('isredeem')
        NetAmount = request.args.get('netamount')
        OrderType = request.args.get('ordertype')
        couponCode = request.args.get('coupon')
        couponDiscount = request.args.get('coupon_discount')
        discountType = request.args.get('discount_type')
        packagingCharge = request.args.get('packaging_charge')
        extraCharge = request.args.get('extra_charge')
        reedemAmount = request.args.get('reedem_amount')
        finalAmount = request.args.get('finalamount')
    except:
        return jsonify({'Variable Not Set': 'Unsuccessful'})

    try:
        conn, cursor = connectDB()

        cursor.execute("""insert into foodfie.Order(CustomerId,StoreId,TotalAmount,PaymentType,NetAmount,
                          Order_Type, Discount_Type, CouponCode, CouponDiscount, WalletReedemAmount,
                          CashCharges, PackagingCharges, FinalAmount) 
                          values ({0}, {1}, {2},'{3}', {4}, '{5}', {6}, '{7}', {8}, {9}, {10}, {11}, {12})
                          """.format(str(CustomerId),str(storeId), str(TotalAmount), str(PaymentType),
                            str(NetAmount),str(OrderType), discountType, couponCode, couponDiscount,
                            reedemAmount, extraCharge, packagingCharge, str(finalAmount)))
        conn.commit()

        # Find the Order Id from the Order Table
        cursor.execute('Select OrderId from foodfie.Order order by OrderId desc limit 1 ;')
        OrderId = cursor.fetchone()[0]

        # Wallet Functionality
        if IsRedeem == 'true':
            TotalAmount = int(TotalAmount)
            redeemWalletBalance(OrderId, CustomerId, TotalAmount)

        # Wallet Redeem Functionality
        if PaymentType == 'cash' or (int(discountType) == 0 and int(couponDiscount) > 0 and len(couponCode) > 0):
            if PaymentType == 'cash':
                SMS_TEXT = """Ohhh!! you have just lost 5% cashback by paying via cash.\n\nGo cashless. Pay via paytm or card(coming soon) and get instant 5% cashback in your Foodfie wallet."""
                SQL = """SELECT CustomerPhoneNo from foodfie.Customer
                         WHERE CustomerId = {0}""".format(CustomerId)
                cursor.execute(SQL)
                mobileNo = cursor.fetchall()[0][0]
                sendSMS(mobileNo, SMS_TEXT, promo=False)
            else:
                pass
        else:
            updateWalletAmount(CustomerId, finalAmount, OrderId)

        # Update Coupon Code functionality
        if int(discountType) == 0 and int(couponDiscount) > 0 and len(couponCode) > 0:
            redeemcoupon(CustomerId, couponCode)

        # Update Inventory
        updateLiveInventory(storeId, OrderId, ItemId, QTY)

        # Foodfie MLM
        # foodfie_MLM.foodfie_MLM(CustomerId, OrderId, int(NetAmount))

        # Send SMS
        sendOrderSMS(CustomerId, OrderId, ItemId, QTY, Price, discountType, IsRedeem, couponCode,
                     couponDiscount, packagingCharge, extraCharge, reedemAmount, TotalAmount, OrderType, PaymentType, NetAmount)

        # Verify no rows are already present in OrderDetail table
        cursor.execute('Select * from foodfie.OrderDetail where OrderId=' + str(OrderId))
        OrderIdExist = cursor.fetchall()
        if OrderIdExist.__len__() == 0:
            for Item, Qt, Pri in zip(ItemId,QTY,Price):
                cursor.execute('insert into foodfie.OrderDetail (OrderId,ItemId,QTY,Price) values (' + str(OrderId) + ',' + str(Item) + ',"' +str(Qt) + '", '+ str(Pri) +');')
                conn.commit()
            return jsonify({'OrderId': OrderId})
        else:
            return jsonify({'Something Weired in Order': 'UnSuccessful'})

    except:
        return jsonify({'Data Issue': 'UnSuccessful'})
    finally:
        conn.commit()
        conn.close()


if __name__ == '__main__':

    #t1 = Thread(target=SMS_Misc.sendFeedbackSMS)
    t2 = Thread(target=application.run)
    #t1.start()
    t2.start()

