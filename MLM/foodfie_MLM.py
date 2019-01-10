from collections import OrderedDict

from Misc.foodfie_db.db import connectDB
from SMS.SMS_Misc import random_MLM_SMS


def foodfie_MLM(customerId, orderId, orderAmount):
    conn, cur = connectDB()

    SQL = """SELECT a.CustomerId, b.CustomerId, c.CustomerId, d.CustomerId, a.CustomerPhoneNo, a.ReferredBy Level1, b.ReferredBy Level2, c.ReferredBy Level3
            FROM foodfie.Customer a
            left join foodfie.Customer b
            on a.ReferredBy = b.CustomerPhoneNo
            left join foodfie.Customer c
            on b.ReferredBy = c.CustomerPhoneNo
            left join foodfie.Customer d
            on c.ReferredBy = d.CustomerPhoneNo
            where a.CustomerId = {0}""".format(customerId)

    cur.execute(SQL)
    friendsDetail = cur.fetchall()[0]

    customerPhoneNo = friendsDetail[4]

    level = 1
    for friendId, friendPhNo in zip(friendsDetail[1:5], friendsDetail[5:8]):

        if friendId:
            SQL = """SELECT MLM_LevelPercent 
                    FROM foodfie.MLM_Level
                    where MLM_LevelId ={}""".format(level)

            cur.execute(SQL)
            levelPercent = cur.fetchall()[0][0]

            SQL = """SELECT WalletId, WalletAmount, date(date_add(LastUpdated, interval 30 Day)) 
                     FROM foodfie.Wallet
                     WHERE CustomerId = {}""".format(friendId)
            cur.execute(SQL)
            walletDetail = cur.fetchall()
            if walletDetail:
                walletId, walletAmount, lastUpdated = walletDetail[0]
                amountTransfer = int((orderAmount * levelPercent) / 100)

                newWalletBalance = walletAmount + amountTransfer

                SQL = """UPDATE foodfie.Wallet
                         SET WalletAmount = {0}
                         WHERE CustomerId = {1}""".format(newWalletBalance, friendId)

                cur.execute(SQL)
                conn.commit()
            else:
                walletId, walletAmount, lastUpdated = walletDetail[0]
                amountTransfer = int(orderAmount * levelPercent / 100)

                newWalletBalance = walletAmount + amountTransfer

                SQL = """INSERT INTO foodfie.Wallet(CustomerId, WalletAmount)
                         VALUES({0}, {1})""".format(friendId, newWalletBalance)

                cur.execute(SQL)
                conn.commit()

            SQL = """INSERT INTO foodfie.WalletDetail(WalletId, OrderId, CustomerId, WalletAmount, WalletBalance, AmountMode)
                     VALUES({0}, {1}, {2}, {3}, {4}, '{5}')""".format(walletId, orderId, friendId, walletAmount, newWalletBalance, 'MLM')

            cur.execute(SQL)
            conn.commit()
            random_MLM_SMS(friendPhNo, level, ['$customerphone$','$orderamount$', '$transferamount$', '$walletbalance$', '$expiredate$'],
                                                 [customerPhoneNo, orderAmount, amountTransfer, newWalletBalance, lastUpdated])
            level += 1
        else:
            return

##foodfie_MLM(3,1,500)
