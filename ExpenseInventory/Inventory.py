import datetime
from collections import OrderedDict
from flask import Blueprint, render_template
from flask import request,jsonify
from flask_cors import CORS, cross_origin
from SMS.SMS_Misc import sendSMS
import pymysql

import config
inventory_api = Blueprint('inventory_api', __name__)
CORS(inventory_api)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


def getInventoryFinished():

    conn, cur = connectDB()
    cur.execute("""select DailyInventoryItemName 
                   from foodfie.DailyInventoryItem;""")
    inventoryName = cur.fetchall()
    l_inventoryName = [cat[0] for cat in inventoryName]
    return l_inventoryName


@inventory_api.route("/inv", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def inv():
    inventoryName = getInventoryFinished()
    return render_template('inv.html', rawItem = inventoryName, commodityName = 'Finished Inventory')


@inventory_api.route("/dailyinventory", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def dailyinventory():
    conn, curs = connectDB()
    curs.execute("""Select StoreName
                    from foodfie.Store""")
    location = curs.fetchall()

    inventoryName = getInventoryFinished()
    return render_template('Inventory.html', rawItem = inventoryName, commodityName = 'Daily Inventory', location = location)


@inventory_api.route("/leftoverinventory", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def leftoverinventory():
    conn, curs = connectDB()
    curs.execute("""Select StoreName
                    from foodfie.Store""")
    location = curs.fetchall()

    inventoryName = getInventoryFinished()
    return render_template('LeftOverInventory.html', rawItem = inventoryName, commodityName = 'Left Over Inventory', location = location)


@inventory_api.route("/submitInventory", methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def result():

    if request.method == 'POST':
        result = request.form.to_dict()
        finalResult = OrderedDict()

        conn, curs = connectDB()
        curs.execute("""Select StoreId
                    from foodfie.Store where storename = '{}'""".format(result['location']))
        storeId = curs.fetchall()[0][0]
        for key, value in result.items():
            if 'Today' in key:
                key = key.replace('Today', '').strip()
                finalResult[key] = value

        for key, qty in finalResult.items():
            if qty != '':
                conn, curs = connectDB()
                curs.execute("""Select DailyInventoryItemId
                                from foodfie.DailyInventoryItem
                                where DailyInventoryItemName = '{}'""".format(key))
                dailyInvId = curs.fetchall()[0][0]
                curs.execute("""insert into foodfie.Daily_Inventory 
                                (DailyInventoryItemId, QTY, StoreId, Prepare_Return) 
                                values({0}, {1}, {2}, 0)""".format(dailyInvId, qty, storeId))
                conn.commit()

                # Update live inventory
                SQL = """SELECT LiveInventoryId, QuantityAvailable, date(LastUpdated)
                         FROM foodfie.LiveInventory
                         WHERE DailyInventoryItemId = {0}
                         AND StoreId = {1}
                    """.format(dailyInvId, storeId)
                curs.execute(SQL)
                liveItemExist = curs.fetchall()

                # If Item in Live Inventory
                if liveItemExist:
                    liveInvId, qtyAvble, lastUpdated = liveItemExist[0]
                    currentDate = datetime.datetime.now().strftime("%Y-%m-%d")
                    # Last updated today?
                    if str(lastUpdated) != currentDate:

                        SQL = """UPDATE foodfie.LiveInventory
                                 SET QuantityAvailable = {0}
                                 WHERE DailyInventoryItemId = {1}
                                 AND StoreId = {2}
                                """.format(qty, dailyInvId, storeId)
                        curs.execute(SQL)
                        conn.commit()

                        SQL = """INSERT INTO foodfie.LiveInventoryAudit(LiveInventoryId, DailyInventoryItemId,
                                                        StoreId, NewQTY)
                                 values({0}, {1}, {2}, {3} )
                                """.format(liveInvId, dailyInvId, storeId, qty)
                        curs.execute(SQL)
                        conn.commit()

                    else:
                        newQTY = qtyAvble + int(qty)
                        SQL = """UPDATE foodfie.LiveInventory
                                 SET QuantityAvailable = {0}
                                 WHERE DailyInventoryItemId = {1}
                                 AND StoreId = {2}
                                """.format(newQTY, dailyInvId, storeId)
                        curs.execute(SQL)
                        conn.commit()

                        SQL = """INSERT INTO foodfie.LiveInventoryAudit(LiveInventoryId, DailyInventoryItemId,
                                                        StoreId, OldQTY, NewQTY)
                                 values({0}, {1}, {2}, {3}, {4} )
                                """.format(liveInvId, dailyInvId, storeId, qtyAvble, newQTY)
                        curs.execute(SQL)
                        conn.commit()
                else:

                    SQL = """INSERT INTO foodfie.LiveInventory(DailyInventoryItemId, QuantityAvailable, StoreId)
                             VALUES({0}, {1}, {2})
                            """.format(dailyInvId, qty, storeId)
                    curs.execute(SQL)
                    conn.commit()

                    # Get Latest LiveInventoryId
                    SQL = """SELECT LiveInventoryId
                             FROM foodfie.LiveInventory
                             ORDER BY 1 DESC
                             LIMIT 1
                        """
                    curs.execute(SQL)
                    liveInvId = curs.fetchall()[0][0]

                    SQL = """INSERT INTO foodfie.LiveInventoryAudit(LiveInventoryId, DailyInventoryItemId,
                                                        StoreId, NewQTY)
                                 values({0}, {1}, {2}, {3} )
                                """.format(liveInvId, dailyInvId, storeId, qty)
                    curs.execute(SQL)
                    conn.commit()

        SMS = 'Inventory for {0}\n'.format(result['location'])
        SMS += ',\n'.join(str(key) + ' : ' + str(value) for key, value in  result.items() if key != 'location')

        curs.execute("""select EmployeeName, EmployeePhoneNo
                    from foodfie.Employee
                    where salary=0""")
        getEmployeeData = curs.fetchall()

        for employeeName, employeePhone in getEmployeeData:
            sendSMS(employeePhone, SMS, promo=False)

    return render_template("Thanks.html")


@inventory_api.route("/leftOverInventory", methods = ['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def set_leftover():

    if request.method == 'POST':
        result = request.form.to_dict()
        finalResult = OrderedDict()

        conn, curs = connectDB()
        curs.execute("""Select StoreId
                    from foodfie.Store where storename = '{}'""".format(result['location']))
        storeId = curs.fetchall()[0][0]
        for key, value in result.items():
            if 'Today' in key:
                key = key.replace('Today', '').strip()
                finalResult[key] = value

        for key, qty in finalResult.items():
            if qty != '':
                conn, curs = connectDB()
                curs.execute("""Select DailyInventoryItemId
                                from foodfie.DailyInventoryItem
                                where DailyInventoryItemName = '{}'""".format(key))
                dailyInvId = curs.fetchall()[0][0]
                curs.execute("""insert into foodfie.Daily_Inventory 
                                (DailyInventoryItemId, QTY, StoreId, Prepare_Return) 
                                values({0}, {1}, {2}, 1)""".format(dailyInvId, qty, storeId))
                conn.commit()

        SMS = 'Left over Inventory for {0}\n'.format(result['location'])
        SMS += ',\n'.join(str(key) + ' : ' + str(value) for key, value in  result.items() if key != 'location')

        curs.execute("""select EmployeeName, EmployeePhoneNo
                    from foodfie.Employee
                    where salary=0""")
        getEmployeeData = curs.fetchall()

        for employeeName, employeePhone in getEmployeeData:
            sendSMS(employeePhone, SMS, promo=False)

    return render_template("Thanks.html")


def updateLiveInventory(storeId, orderId, l_itemId, l_qty):
    """
    This function will update the live inventory
    :param storeId:
    :param orderId:
    :param l_itemId:
    :param l_qty:
    :return:
    """
    conn, curs = connectDB()
    for item, qty in zip(l_itemId, l_qty):

        SQL = """SELECT a.LiveInventoryId, a.DailyInventoryItemId, a.StoreId, 
                        a.QuantityAvailable, d.ItemId, d.Pieces
                FROM foodfie.LiveInventory a
                join foodfie.DailyInventoryItemDetail c
                on a.DailyInventoryItemId = c.DailyInventoryItemId
                join foodfie.Item d
                on c.ItemId = d.ItemId
                and a.StoreId = {0}
                and d.ItemId = {1}
            """.format(storeId, item)
        curs.execute(SQL)
        itemDetail = curs.fetchall()

        if itemDetail:
            inventoryId, inventoryItemId, store, qtyAvailable, itemId, pieces = itemDetail[0]
            totalQTY = int(qty) * pieces
            updateQTY = qtyAvailable - totalQTY

            SQL = """UPDATE foodfie.LiveInventory
                     SET QuantityAvailable = {0}, LastUpdated = CURRENT_TIMESTAMP
                     WHERE LiveInventoryId = {1}
                     AND StoreId = {2}
                     AND DailyInventoryItemId = {3}
                    """.format(updateQTY, inventoryId, store, inventoryItemId)

            curs.execute(SQL)
            conn.commit()

            # Update LiveInventory Audit Table
            SQL = """INSERT INTO foodfie.LiveInventoryAudit(LiveInventoryId, DailyInventoryItemId,
                                                                 StoreId, OrderId, ItemId, QTY, TotalPieces, 
                                                                 OldQTY, NewQTY)
                     VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})
                  """.format(inventoryId, inventoryItemId, store, orderId, itemId,
                             qty, totalQTY, qtyAvailable, updateQTY)

            curs.execute(SQL)
            conn.commit()



