import time
import argparse
import os
import sys
import logging

_this_dir = os.path.dirname(os.path.abspath(__file__))
to_add = os.path.abspath(_this_dir + '/../..')  # for 'foodfie'
if to_add not in sys.path:
    sys.path.insert(0, to_add)

if 1:
    from Misc.foodfie_db import db
    from SMS.SMS_Misc import randomSMS
    from Misc import logger

logg = logging.getLogger(__name__)
logg = logger.setLogger(logg)


def sendWalletReminder():

    # Get all the Customer whose Wallet Balance is more than 0
    logg.info("=> Sending Wallet Reminder")
    conn, curs = db.connectDB()
    timestr = time.strftime("%Y%m%d")

    SQL = """select b.CustomerPhoneNo, b.CustomerId, a.WalletAmount, a.LastUpdated, date(date_add(a.LastUpdated, Interval 30 DAY))
            from foodfie.Wallet a
            join foodfie.Customer b
            on a.CustomerId = b.CustomerId
            and a.WalletAmount > 0
            and date_add(a.LastUpdated, Interval 30 DAY) between current_date() and date_add(current_date(),interval 7 day)"""
    walletCustomerDetail = db.getData(SQL)

    # Insert campaign in WalletCampaign table
    logg.info("=> New campaign created: {0}".format('Campaign_' + str(timestr)))
    SQL = """insert into foodfie_analysis.WalletCampaign(WalletCampaignName) 
             values('{0}')""".format('Campaign_' + str(timestr))

    curs.execute(SQL)
    conn.commit()

    # Get Campaign Id
    SQL = """Select WalletCampaignId 
             from foodfie_analysis.WalletCampaign
             order by 1 desc
             limit 1"""
    curs.execute(SQL)
    campaginId = curs.fetchall()[0][0]

    for customer in walletCustomerDetail:

        customerPhoneNo = customer[0]
        walletAmount = customer[2]
        customerId = customer[1]

        # Send SMS to customer
        logg.info("Sending SMS to CustomerId: {0} whose wallet amount is: {1}".format(customerId, walletAmount))
        randomSMS(customerPhoneNo, campaignId= 1, needToReplace = ['$walletbalance$', '$walletdate$'], replaceWith = [walletAmount, customer[4]] )

        # Insert campaign detail in WalletCampaignDetail table
        logg.info("=>Inserted into CampaignDetail: CampaignId- {0}, CustomerId -{1}".format(campaginId, customerId))
        SQL = """insert into foodfie_analysis.WalletCampaignDetail(WalletCampaignId, CustomerId)
                 values({0}, {1})""".format(campaginId, customerId)

        curs.execute(SQL)
        conn.commit()


def walletReturnCustomer():
    logg.info("=> Finding return customers")
    conn, curs = db.connectDB()

    SQL = """Select WalletCampaignId 
             from foodfie_analysis.WalletCampaign
             order by 1 desc
             limit 1"""
    curs.execute(SQL)
    campaginId = curs.fetchall()[0][0]
    logg.info("CampaignId: {0}".format(campaginId))
    SQL = """Select CustomerId 
             from foodfie_analysis.WalletCampaignDetail
             where WalletCampaignId = {0}
             """.format(campaginId)
    curs.execute(SQL)
    customerIds = [item[0] for item in curs.fetchall()]

    SQL = """Select CustomerId, TotalAmount, NetAmount, OrderTime
             from foodfie.Order
             where date(OrderTime) = current_date()
             and TotalAmount <> NetAmount
          """
    curs.execute(SQL)
    customerCurrentDetail = curs.fetchall()
    if customerCurrentDetail:
        logg.info("=> Returned Customers:")
        for customer in customerCurrentDetail:
            customerId = customer[0]
            customerTotalAmount = customer[1]
            customerNetAmount = customer[2]
            customerReturnDate = customer[3]

            if customerId in customerIds:
                logg.info("CustomerId: {0}, TotalAmount: {1}, NetAmount:{2}, ReturnDate: {3}".format(customerId, customerTotalAmount, customerNetAmount, customerReturnDate))
                # Insert return customer to WalletCampaignReturn
                SQL = """insert into foodfie_analysis.WalletCampaignReturn(WalletCampaignId, ReturnCustomerId,OldWalletBalance, NewWalletBalance, TotalAmount, NetAmount, WalletCampaignReturnDate)
                             values({0}, {1}, {2}, {3}, {4}, {5}, '{6}')""".format(campaginId, customerId, 0, 0,      customerTotalAmount, customerNetAmount, customerReturnDate)
                curs.execute(SQL)
                conn.commit()
    else:
        logg.info("No data found")

## Everyday at 11.30 we will be running a job and will check how many people are coming back after wallet msg


def walletReminderTodayExhaust():
    logg.info("=> Sending Reminder")
    conn, curs = db.connectDB()
    SQL = """select b.CustomerPhoneNo, WalletId, b.CustomerId, WalletAmount, date(LastUpdated), date(date_add(date(LastUpdated), interval 30 DAY)) 
            from foodfie.Wallet a
            join foodfie.Customer b
            on a.CustomerId = b.CustomerId
            and date_add(date(LastUpdated), interval 30 DAY)  = current_date() #between current_date() - 1 and current_date()
            and WalletAmount > 0
          """
    curs.execute(SQL)
    walletCustomerDetail = curs.fetchall()
    for customer in walletCustomerDetail:

        customerPhoneNo = customer[0]
        customerId = customer[2]
        walletAmount = customer[3]
        expireOn =  customer[5]

        # Send SMS to customer
        logg.info("Sending SMS to CustomerId: {0} whose wallet amount is: {1}, Expires on: {2}".format(customerId, walletAmount, expireOn))
        randomSMS(customerPhoneNo, campaignId= 1, needToReplace = ['$walletbalance$', '$walletdate$'], replaceWith = [walletAmount, expireOn] )


def walletUpdateBalanceIfUnused():
    logg.info("=>Updating Wallet Balance")
    SQL = """select WalletId, CustomerId, WalletAmount, date(LastUpdated), date(date_add(LastUpdated, interval 30 DAY)) 
            from foodfie.Wallet
            where LastUpdated < date_sub(current_date(),interval 30 day) 
            and WalletAmount > 0
          """
    conn, curs = db.connectDB()
    curs.execute(SQL)

    customerIds = curs.fetchall()
    logg.info("Total no of Customer: {0}".format(len(customerIds)))
    if customerIds:
        for customer in customerIds:
            logg.info("=>Modifying wallet amount for CustomerId: {0}, WalletId: {1}, WalletAmount: {2} and Last updated: {3}".format(customer[1], customer[0], customer[2], customer[3]))

            SQL = """update foodfie.Wallet
            set WalletAmount = 0
            where WalletId = {0}
            and CustomerId = {1}""".format(customer[0], customer[1])

            curs.execute(SQL)

            logg.info("=> Inserting row in foodfie.WalletDetail table. CustomerId: {0}, WalletId: {1}, WalletBalance: {2}".format(customer[1], customer[0], 0))

            SQL = """insert into foodfie.WalletDetail(WalletId, CustomerId, WalletBalance)
            values({0},{1}, 0)""".format(customer[0], customer[1])
            curs.execute(SQL)
            conn.commit()


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("--sendReminderMonday", help="Send Reminder to customer", action="store_true")
    ap.add_argument("--returnCustomer", help="Send Reminder to customer", action="store_true")
    ap.add_argument("--sendReminderDaily", help="Send Reminder to customer", action="store_true")
    ap.add_argument("--updateBalance", help="Send Reminder to customer", action="store_true")

    args = ap.parse_args()
    if args.sendReminderMonday:
        sendWalletReminder()
    elif args.returnCustomer:
        walletReturnCustomer()
    elif args.sendReminderDaily:
        walletReminderTodayExhaust()
    elif args.updateBalance:
        walletUpdateBalanceIfUnused()


