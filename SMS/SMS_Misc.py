import time
import requests
import pymysql
import datetime
import random

import config


def connectDB():
    conn = pymysql.connect(host = config.host, port=config.port, user= config.user, password = config.password, db= config.db)
    cur = conn.cursor()
    return conn, cur


def sendSMS(mobileNo, message, promo = True):

    InitialURL = config.url
    Type = 'sendhttp.php?'
    AuthKey = config.authkey
    Sender = config.sender

    if promo:
        url = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobiles=' + str(mobileNo) + '&message= '+ str(message) + str(config.message) +'&sender='+ str(Sender) + '&route=4' + '&country=91'
    else:
        url = str(InitialURL) + str(Type) + 'authkey=' + str(AuthKey) + '&mobiles=' + str(mobileNo) + '&message= '+ str(message)  +'&sender='+ str(Sender) + '&route=4' + '&country=91'
    output = requests.get(url)
    return output.text


def randomSMS(mobileNo, campaignId, needToReplace, replaceWith):
    conn, curs = connectDB()

    curs.execute("""Select CampaignMessage from foodfie_analysis.CampaignMessages
                    where CampaignMessageId = {0}""".format(campaignId))
    message = list(curs.fetchall())
    random.shuffle(message)
    messageSend = random.choice(message)[0]
    if needToReplace:
        for rep, repWith in zip(needToReplace, replaceWith):
            if rep in messageSend:
                messageSend = messageSend.replace(rep, str(repWith))

    sendSMS(mobileNo, messageSend, promo=False)


def randomCampaignSMS(customerId, campaignId, campaignMessageId, needToReplace = '', replaceWith = '', promo = True):
    conn, curs = connectDB()

    # Verify Mobile No is blacklisted or not?
    SQL = """SELECT CustomerId
             FROM foodfie_analysis.BlacklistNumber
             WHERE customerid = {0}""".format(customerId)
    curs.execute(SQL)
    noInBlacklist = curs.fetchall()

    if noInBlacklist:
        pass

    else:
        # Verify we have not send the promo message in last 3 days
        if promo:
            SQL = """SELECT CampaignCustomerId 
                     from foodfie_analysis.CampaignSMSSent
                     where CampaignSMSSentTime >= date_sub(current_date(), interval 3 day)"""
            curs.execute(SQL)
            msgSentInLast3Days = [cust[0] for cust in curs.fetchall()]

            if customerId in msgSentInLast3Days:
                return

        curs.execute("""Select CampaignMessage 
                        from foodfie_analysis.CampaignMessages
                        where CampaignMessageId = {0}""".format(campaignMessageId))
        message = list(curs.fetchall())
        random.shuffle(message)
        messageSend = random.choice(message)[0]
        if needToReplace:
            for rep, repWith in zip(needToReplace, replaceWith):
                if rep in messageSend:
                    messageSend = messageSend.replace(rep, str(repWith))

        SQL = """INSERT INTO foodfie_analysis.CampaignSMSSent(CampaignId, CampaignMessage, CampaignCustomerId)
                 VALUES({0}, '{1}', {2})""".format(campaignId, messageSend, customerId)
        curs.execute(SQL)
        conn.commit()

        SQL = """SELECT CustomerPhoneNo
                 FROM foodfie.Customer
                 WHERE CustomerId = {0}""".format(customerId)
        curs.execute(SQL)
        mobileNo = curs.fetchall()[0][0]

        sendSMS(mobileNo, messageSend, promo=False)
        # https://goo.gl/forms/2HrtXhtwlfPBcVLH3


def random_MLM_SMS(mobileNo, levelId, needToReplace, replaceWith):
    conn, curs = connectDB()

    SQL = """SELECT MLM_Messages 
             FROM foodfie.MLM_Message
             where MLM_LevelId = {}""".format(levelId)

    curs.execute(SQL)
    message = list(curs.fetchall())
    random.shuffle(message)
    messageSend = random.choice(message)[0]
    if needToReplace:
        for rep, repWith in zip(needToReplace, replaceWith):
            if rep in messageSend:
                messageSend = messageSend.replace(rep, str(repWith))
    sendSMS(mobileNo, messageSend, promo=False)


def sendOrderSMS(CustomerId, orderId, ItemId, QTY, Price, discountType, IsRedeem, couponCode,
                     couponDiscount, packagingCharge, extraCharge, reedemAmount, TotalAmount, OrderType,
                 PaymentType, NetAmount):

    conn, cur = connectDB()
    SMS_TEXt = """WOHOO!!! Your order is placed.\n Your Order No: {0}.\nYour Order is\n""".format(orderId)
    itemDetail = ''
    for item,qt in zip(ItemId, QTY):

        SQL = """SELECT b.CategoryName, a.ItemName, a.Quantity, a.ItemPrice
                FROM foodfie.`Item` a
                join foodfie.Category b
                on a.CategoryId = b.CategoryId
                and a.ItemId = {0}
                """.format(item)
        cur.execute(SQL)
        itemD = cur.fetchall()[0]
        itemDetail += itemD[0] + '-' + itemD[1] + ' ' + itemD[2] + ' X ' + qt + '=' + str(int(itemD[3]) * int(qt)) + '\n'

    SMS_TEXt += itemDetail
    SMS_TEXt += 'Total Amount: ' + str(TotalAmount) + '\n'

    SQL = """SELECT WalletAmount 
             FROM foodfie.Wallet
             WHERE CustomerId = {0}""".format(CustomerId)
    cur.execute(SQL)
    balance = cur.fetchall()

    if balance:
        SMS_TEXt += 'Wallet Balance: ' + str(balance[0][0]) +'\n'

    if IsRedeem == 'true':
        SMS_TEXt += 'Redeem Amount: ' + str(reedemAmount) + '\n'

    if len(couponCode) > 0 and int(couponDiscount) > 0:
        SMS_TEXt += 'Coupon Code: ' + str(couponCode) +'\n'

    if OrderType == 'takeaway':
        SMS_TEXt += 'Packaging Charges: ' + str(packagingCharge) + '\n'

    SMS_TEXt += 'Net Amount: ' + str(NetAmount) + '\n'

    SQL = """SELECT CustomerPhoneNo
             FROM foodfie.Customer
             WHERE CustomerId = {}""".format(CustomerId)
    cur.execute(SQL)
    phoneNo = cur.fetchall()[0][0]

    sendSMS(phoneNo, SMS_TEXt)


