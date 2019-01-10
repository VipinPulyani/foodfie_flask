from flask import Blueprint
import pymysql
from flask import Blueprint
from flask import request, jsonify
from flask_cors import CORS, cross_origin

import config
from SMS.TransactionSMS import walletSMS

wallet_api = Blueprint('wallet_api', __name__)
CORS(wallet_api)


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


def updateWalletAmount(CustomerId, TotalAmount, OrderId):

    try:
        conn, cursor = connectDB()
        amount = round(int(TotalAmount) * 0.05)  # 5% of total amount
        cursor.execute('select WalletId from foodfie.Wallet where CustomerId = ' + CustomerId)
        customerExist = cursor.fetchall()

        if not customerExist:
            cursor.execute('insert into foodfie.Wallet(CustomerId, WalletAmount) values(' + str(CustomerId) + ',' + str(amount) + ');')
            conn.commit()
            cursor.execute('select WalletId from foodfie.Wallet where CustomerId = ' + CustomerId + ';')
            walletId = cursor.fetchall()[0][0]
            cursor.execute("""insert into foodfie.WalletDetail(WalletId, OrderId, CustomerId, WalletAmount, WalletBalance, BillAmount)
            values({0}, {1}, {2}, {3}, {4}, {5})""".format(str(walletId), str(OrderId), str(CustomerId), str(amount), str(amount), str(TotalAmount)))
            conn.commit()

            # Wallet SMS to custonmer
            walletSMS(CustomerId, amount, amount)

        else:
            cursor.execute('select WalletId, WalletAmount from foodfie.Wallet where CustomerId = ' + str(CustomerId) + ';')
            data = cursor.fetchall()[0]
            walletId, walletAmount = data[0], data[1]
            newAmount = walletAmount + amount
            cursor.execute(""" update foodfie.Wallet
                               set WalletAmount = {0}, LastUpdated = current_timestamp()
                               where WalletId =  {1}
                               and CustomerId = {2};""".format(str(newAmount), str(walletId), str(CustomerId)))
            cursor.execute("""insert into foodfie.WalletDetail(WalletId, OrderId, CustomerId, WalletAmount, WalletBalance, BillAmount)
            values({0}, {1}, {2}, {3}, {4}, {5})""".format(str(walletId), str(OrderId), str(CustomerId), str(amount), str(newAmount), str(TotalAmount)))
            conn.commit()

            # Wallet SMS to custonmer
            walletSMS(CustomerId, amount, newAmount)

        return jsonify({'Data Updated': 'Successful'})
    except:
        return jsonify({'Data Issue': 'UnSuccessful'})
    finally:
        conn.close()


@wallet_api.route("/api/v1.0/getwalletbalance", methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getWalletBalance():

    try:
        customerId = request.args.get('customerid')
    except:
        return jsonify({'Variable Not Set': 'Unsuccessful'})
    try:
        conn, cursor = connectDB()
        cursor.execute('select WalletAmount from foodfie.Wallet where CustomerId = ' + str(customerId))
        walletAmount = cursor.fetchall()
        if walletAmount:
            return jsonify({'WalletAmount': walletAmount[0][0]})
        else:
            return jsonify({'WalletAmount': 0})
    except:
        return jsonify({'Data Issue': 'UnSuccessful'})
        conn.close()


#@wallet_api.route("/api/v1.0/redeemwalletbalance", methods = ['POST'])
#@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def redeemWalletBalance(orderId, customerId, totalAmount):

#    try:
#        orderId = request.args.get('orderid')
#        customerId = request.args.get('customerid')
#        totalAmount = int(request.args.get('amount'))
#    except:
#        return jsonify({'Variable Not Set': 'Unsuccessful'})

    try:
        conn, cursor = connectDB()
        cursor.execute('select WalletId, WalletAmount from foodfie.Wallet where CustomerId = ' + str(customerId))
        data = cursor.fetchall()
        if data:
            walletId = data[0][0]
            walletAmount = data[0][1]
            if totalAmount >= walletAmount:
                balance = totalAmount - walletAmount
                cursor.execute("""update foodfie.Wallet
                               set WalletAmount = 0
                               where WalletId =  {0}
                               and CustomerId = {1};""".format(str(walletId), str(customerId)))
                cursor.execute("""insert into foodfie.WalletDetail(WalletId, OrderId, CustomerId, WalletAmount, WalletBalance, BillAmount)
                                values({0}, {1}, {2}, {3}, {4}, {5})""".format(str(walletId), str(orderId), str(customerId), '-' + str(walletAmount), 0, str(totalAmount)))
                conn.commit()
                return jsonify({'WalletBalance': 0, 'CustomerBalance': balance})
            else:
                balance = walletAmount - totalAmount
                cursor.execute("""update foodfie.Wallet
                               set WalletAmount = {0}
                               where WalletId =  {1}
                               and CustomerId = {2};""".format(str(balance), str(walletId), str(customerId)))

                cursor.execute("""insert into foodfie.WalletDetail(WalletId, OrderId, CustomerId, WalletAmount, WalletBalance, BillAmount)
                                values({0}, {1}, {2}, {3}, {4}, {5})""".format(str(walletId), str(orderId), str(customerId), '-' + str(totalAmount), balance, str(totalAmount)))
                conn.commit()
                return jsonify({'WalletBalance': balance, 'CustomerBalance': 0})
        else:
            return jsonify({'WalletBalance': 0, 'CustomerBalance': totalAmount})
    except:
        return jsonify({'Data Issue': 'UnSuccessful'})
    finally:
        conn.close()
