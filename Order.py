import requests
import random
import pymysql
from collections import OrderedDict
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask import Blueprint, request


from SMS.SMS_Misc import sendSMS
import config
OrdDet_API = Blueprint('OrdDet_api', __name__ )
CORS(OrdDet_API)

#
# @OrdDet_API.route('/api/v1.0/order')
# @cross_origin(origin='*',headers=['Content- Type','Authorization'])
# def updateOrder():
#     pass
#     #conn, cur = connectDB()
#
#     #cur.execute('insert into foodfie.Order')


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


@OrdDet_API.route('/api/v1.0/updateitem', methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def updateOrder():
    try:
        OrderId = request.args.get('orderid')
        ItemId = request.args.get('itemid')
        ItemStatus = request.args.get('itemstatus')

    except:
        return jsonify({'Variable Not Set': 'Unsuccessful'})

    try:
        conn, cursor = connectDB()
        cursor.execute("""update foodfie.OrderDetail 
                          set ItemStatus = {0} 
                          where OrderId = {1} 
                          and ItemId= {2}""".format(ItemStatus, OrderId, ItemId))
        conn.commit()
        return jsonify({'Data Updated': 'Successful'})
    except:
        return jsonify({'Error': -1})
    finally:
        conn.commit()
        conn.close()


@OrdDet_API.route('/api/v1.0/changestatus', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def changestatus():
    """ Will be using this function while we change status of Order
        from New --> Processing --> Cancelled/Completed
        2   Processing
        3   Cancelled
        4   Scheduled
        5   Completed
    """
    statusType = request.args.get('statustype')
    orderId = request.args.get('orderid')

    conn, curs = connectDB()

    sql = """Update foodfie.Order
             set orderstatus = {0}, {1}
             where orderid = {2}
            """.format(statusType,'OrderProcessStarted = CURRENT_TIMESTAMP' if statusType == '2'
                                       else 'OrderEndTime = CURRENT_TIMESTAMP', orderId)
    curs.execute(sql)
    conn.commit()
    curs.execute("""Select CustomerPhoneNo from foodfie.Customer
                    where CustomerId = (Select CustomerId from foodfie.Order 
                    where OrderId = {0})""".format(orderId))
    mobileNo = curs.fetchall()[0][0]

    curs.execute("""Select OrderMessage from foodfie.OrderMessage
                    where OrderStatusId = {0}""".format(statusType))
    message = list(curs.fetchall())
    random.shuffle(message)
    messageSend = random.choice(message)[0]

    sendSMS(mobileNo, messageSend)
    return jsonify({'Message': 'Successfully sent'})


@OrdDet_API.route('/api/v1.0/getorder', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def newOrder():
     try:
        orderstatus = request.args.get('orderstatus')
        storeId = request.args.get('storeid')
        orderId = request.args.get('orderid')
     except:
        return jsonify({'Variable Not Set': 'Unsuccessful'})

     try:
        conn, cursor = connectDB()
        cursor.execute(""" Select a.OrderId, a.ItemId, d.Order_Type, c.CategoryName, b.ItemName,                             a.Qty, a.OrderDetailTime, d.OrderSource, d.NetAmount, d.PaymentType
                            from foodfie.OrderDetail a
                            join foodfie.Item b
                            on a.ItemId = b.ItemId
                            and a.ItemStatus in ( {0})
                            join foodfie.Category c
                            on b.CategoryId = c.CategoryId
                            join foodfie.Order d
                            on a.OrderId = d.OrderId
                            AND d.storeid = {1}
                            {2}
        """.format(orderstatus, storeId, 'AND d.orderid >' + str(orderId) if orderId else '') + (" Order by a.OrderId desc Limit 30" if orderstatus == '5' or orderstatus == '3' else ";"))

        data = cursor.fetchall()

        items = OrderedDict()
        for item in data:
            if item[0] not in items.keys():
                i = 1
                items[item[0]] = OrderedDict()
                items[item[0]]['OrderDetail'] = OrderedDict()
                for x,y in zip(('OrderId', 'orderstatus', 'OrderDetailTime', 'OrderSource', 'NetAmount', 'PaymentType'), (item[0], item[2], item[6], item[7], item[8], item[9])):
                    items[item[0]]['OrderDetail'][x] = y
                items[item[0]]['OrderItems'] = OrderedDict()

            items[item[0]]['OrderItems'][i] = OrderedDict()
            for x,y in zip(('ItemId', 'CategoryName', 'ItemName', 'Qty'), (item[1], item[3], item[4], item[5])):
                items[item[0]]['OrderItems'][i][x] = y
            i += 1
        return jsonify({'Order': items})
     except:
         return jsonify({'Data Issue': 'UnSuccessful'})
     finally:
        conn.close()


@OrdDet_API.route('/api/v1.0/itemsummary', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def itemsummary():
    storeId = request.args.get('storeid')
    conn, cursor = connectDB()
    cursor.execute("""select c.CategoryName, b.ItemName, b.Quantity, cast(sum(a.QTY) as SIGNED) TotalQTY
                    from foodfie.OrderDetail a
                    join foodfie.Item b 
                    on a.ItemId = b.ItemId
                    and a.ItemStatus = 1
                    join foodfie.Category c
                    on b.CategoryId = c.CategoryId
                    join foodfie.Order d
                    on a.Orderid = d.OrderId
                    and d.storeid = {0} 
                    group by b.ItemId, c.CategoryName, b.ItemName, b.Quantity
                    """.format(storeId))
    itemData = cursor.fetchall()

    l_itemdata = [dict((x,y) for x,y in zip(('CategoryName', 'ItemName', 'Type', 'TotalQTY'),(item[0], item[1], item[2], item[3], item[0]))) for item in itemData]

    return jsonify({'ItemSummary': l_itemdata})


@OrdDet_API.route('/api/v1.0/ordercount', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def orderCount():
    storeId = request.args.get('storeid')
    conn, curs = connectDB()
    curs.execute("""select count(*) 
                    from foodfie.Order
                    where orderstatus = 1
                    and storeid= {0}""".format(storeId))
    orderData = curs.fetchall()[0][0]
    return jsonify({'OrderCount': orderData})


@OrdDet_API.route('/api/v2.0/getorder', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def newOrders():
     try:
        orderstatus = request.args.get('orderstatus')
     except:
        return jsonify({'Variable Not Set': 'Unsuccessful'})

     try:
        conn, cursor = connectDB()
        cursor.execute(""" Select a.OrderId, a.ItemId, d.Order_Type, c.CategoryName, b.ItemName, b.Quantity, a.Qty, a.OrderDetailTime
                            from foodfie.OrderDetail a
                            join foodfie.Item b
                            on a.ItemId = b.ItemId
                            and a.ItemStatus = '{0}'
                            join foodfie.Category c
                            on b.CategoryId = c.CategoryId
                            join foodfie.Order d
                            on a.OrderId = d.OrderId
        """.format(orderstatus) + (" and d.OrderId > ((select max(OrderId) from foodfie.Order) - 20) Order by a.OrderId desc;" if orderstatus == 'completed' or orderstatus == 'cancelled' else "Order by a.OrderId;"))

        print(""" Select a.OrderId, a.ItemId, d.Order_Type, c.CategoryName, b.ItemName, b.Quantity, a.Qty, a.OrderDetailTime
                            from foodfie.OrderDetail a
                            join foodfie.Item b
                            on a.ItemId = b.ItemId
                            and a.ItemStatus = '{0}'
                            join foodfie.Category c
                            on b.CategoryId = c.CategoryId
                            join foodfie.Order d
                            on a.OrderId = d.OrderId
        """.format(orderstatus) + (" and d.OrderId > ((select max(OrderId) from foodfie.Order) - 20) Order by a.OrderId desc;" if orderstatus == 'completed' or orderstatus == 'cancelled' else "Order by a.OrderId ;"))
        data = cursor.fetchall()

        items = OrderedDict()
        for item in data:
            if item[0] not in items.keys():
                i = 1
                items[item[0]] = OrderedDict()
            items[item[0]][i] = OrderedDict()
            for x,y in zip(('OrderId', 'ItemId', 'orderstatus', 'CategoryName', 'ItemName', 'ItemType', 'Qty', 'OrderDetailTime'), item):
                items[item[0]][i][x] = y
            i += 1

        # items = OrderedDict()
        # for item in data:
        #     if item[0] not in items.keys():
        #         i = 1
        #         items[item[0]] = OrderedDict()
        #     items[item[0]][i] = OrderedDict()
        #     for x,y in zip(('OrderId', 'ItemId', 'orderstatus', 'CategoryName', 'ItemName', 'Qty', 'OrderDetailTime'), item):
        #         items[item[0]][i][x] = y
        #     i += 1
        return jsonify({'Order': items})
     except:
         return jsonify({'Data Issue': 'UnSuccessful'})
     finally:
        conn.close()
