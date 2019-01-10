import os
import sys
import logging

_this_dir = os.path.dirname(os.path.abspath(__file__))
to_add = os.path.abspath(_this_dir + '/..')  # for 'qa_py'
if to_add not in sys.path:
    sys.path.insert(0, to_add)

if 1:
    from Misc import logger
    from SMS.SMS_Misc import sendSMS
    from Misc.foodfie_db.db import connectDB

logg = logging.getLogger(__name__)
logg = logger.setLogger(logg)

logg.info("=> Sending Feedback SMS's")
phoneNoDetail = []
conn, cur = connectDB()
# All the Customer which order something
cur.execute("""SELECT a.OrderId,a.CustomerId, b.CustomerPhoneNo, a.OrderTime
                FROM foodfie.`Order` a
                join foodfie.Customer b
                on a.CustomerId = b.CustomerId
                and a.FeedbackSMS = 0
                and a.OrderTime < date_sub(current_timestamp(), interval 1 hour)
            """)
customerDetail = cur.fetchall()
if customerDetail:
    for orderId, customerId, phoneNo, orderTime in customerDetail:
        # Trigger SMS when CurrentTime > OrderTime by 30 mins and more
        message = """Hey, Thank you for being at Foodfie. Did we twist your tongue with our cuisines? Either yes or No, do share your feedback or review us. \nZomato: https://goo.gl/oVNNS7\nFacebook: https://goo.gl/9EDEuQ\nGoogle: https://goo.gl/fBkyYn\nMsg to owner: https://goo.gl/PDy4Wd"""
        # Avoid multiple feedback SMS to same phoneno
        if phoneNo not in phoneNoDetail:
            logg.info("Sending SMS to customerid: {0}".format(customerId))
            sendSMS(phoneNo, message, promo=False)
            phoneNoDetail.append(phoneNo)
        try:
            cur.execute("""update foodfie.`Order`
                    set FeedbackSMS = 1
                    where orderid = {}
                """.format(orderId))
            cur.execute('commit')
        except:
            pass
else:
    logg.info("=> No customer for feedback SMS")
