import os
import sys

_this_dir = os.path.dirname(os.path.abspath(__file__))
to_add = os.path.abspath(_this_dir + '/../..')  # for 'qa_py'
if to_add not in sys.path:
    sys.path.insert(0, to_add)

if 1:
    from Misc.foodfie_db.db import connectDB
    from SMS.SMS_Misc import sendSMS


def sendSalesNotification():

    date, totalSales, totalOrders = 0,0,0
    candorSales, candorOrders, infotechCard, infotechSwiggy, infotechSales, infotechSales = 0,0,0,0,0,0
    candorCash, candorPaytm, candorCard, candorSwiggy, infotechCash, infotechPaytm = 0,0,0,0,0,0

    con, cur = connectDB()
    cur.execute("""select EmployeeName, EmployeePhoneNo
                    from foodfie.Employee
                    where salary=0""")
    getEmployeeData = cur.fetchall()

    cur.execute("""select date(OrderTime), sum(NetAmount), count(*)
                    from foodfie.Order
                    where date(OrderTime) = current_date()
                    group by date(OrderTime)
                """)
    getTotalSales = cur.fetchall()[0]
    date, totalSales, totalOrders = getTotalSales

    cur.execute("""select date(OrderTime), StoreId, sum(NetAmount), count(*)
                    from foodfie.Order
                    where date(OrderTime) = current_date()
                    group by date(OrderTime), StoreId
                """)
    getSalesPerStore = cur.fetchall()

    for item in getSalesPerStore:
        if item[1] == 1:
            candorSales = item[2]
            candorOrders = item[3]
        elif item[1] == 2:
            infotechSales = item[2]
            infotechOrders = item[3]

    cur.execute("""select date(OrderTime) , StoreId, PaymentType, sum(NetAmount)
                    from foodfie.Order
                    where date(OrderTime) = current_date()
                    group by date(OrderTime), StoreId, PaymentType
                    """)

    getSalesPaymentType = cur.fetchall()

    for item in getSalesPaymentType:
        if item[1] == 1 and item[2] == 'cash':
            candorCash = item[3]
        elif item[1] == 1 and item[2] == 'paytm':
            candorPaytm = item[3]
        elif item[1] == 1 and item[2] == 'card':
            candorCard = item[3]
        elif item[1] == 1 and item[2] == 'swiggy':
            candorSwiggy = item[3]
        elif item[1] == 2 and item[2] == 'cash':
            infotechCash = item[3]
        elif item[1] == 2 and item[2] == 'paytm':
            infotechPaytm = item[3]
        elif item[1] == 2 and item[2] == 'card':
            infotechCard = item[3]
        elif item[1] == 2 and item[2] == 'swiggy':
            infotechSwiggy = item[3]

    for employeeName, employeePhone in getEmployeeData:

        Message = """Hi $name$, Sales for foodfie {0}:
                 Total Sales: {1}
                 Total Orders: {2}

                 Sale for Candor:
                 Cash: {3}
                 Paytm: {4}
                 Card: {5}
                 Swiggy: {6}
                 Total: {7}
                 Orders: {8}

                 Sale for Infotech:
                 Cash: {9}
                 Paytm: {10}
                 Card: {11}
                 Swiggy: {12}
                 Total: {13}
                 Orders: {14}
                """.format(date, totalSales, totalOrders,
                           candorCash, candorPaytm, candorCard, candorSwiggy, candorSales, candorOrders,
                           infotechCash, infotechPaytm, infotechCard, infotechSwiggy, infotechSales, infotechOrders
                           )

        Message = Message.replace('$name$', employeeName)
        MobileNo = employeePhone
        sendSMS(MobileNo, Message)


# def dailyInventory():
#
#     con, cur = connectDB()
#     cur.execute("""SELECT a.DailyInventoryItemId ,b.DailyInventoryItemName, a.StoreId, a.QTY, a.InsertedTime
#                     FROM foodfie.Daily_Inventory a
#                     join foodfie.DailyInventoryItem b
#                     on a.DailyInventoryItemId = b.DailyInventoryItemId
#                     and date(a.InsertedTime) = current_date()""")
#     inventoryData = cur.fetchall()
#
#     Message = [item for item in inventoryData]
#     pass
#
# dailyInventory()
sendSalesNotification()
