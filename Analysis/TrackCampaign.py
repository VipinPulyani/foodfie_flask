import os
import sys
import logging


_this_dir = os.path.dirname(os.path.abspath(__file__))
to_add = os.path.abspath(_this_dir + '/..')  # for 'qa_py'
if to_add not in sys.path:
    sys.path.insert(0, to_add)

if 1:
    from Misc import logger
    from Misc.foodfie_db.db import connectDB

logg = logging.getLogger(__name__)
logg = logger.setLogger(logg)

conn, curs = connectDB()


def trackCampaign():
    """
    Track campaign
    """
    logg.info("=>Tracking Campaign")
    # Get Campaign Detail
    SQL = """SELECT a.CampaignId, a.CustomerSegmentId
            FROM foodfie_analysis.Campaign a
            JOIN foodfie_analysis.CustomerSegments b
            ON a.CustomerSegmentId = b.CustomerSegmentId 
            AND a.IsEnabled  = 1"""

    curs.execute(SQL)
    campaignDetails = curs.fetchall()

    for campaignDetail in campaignDetails:

        campaignId, customerSegment = campaignDetail

        SQL = """SELECT CampaignCustomerId 
                 FROM foodfie_analysis.CampaignSMSSent
                 WHERE campaignId = {0}
                 AND CampaignSMSSentTime >= date_sub(current_date(), interval 7 day)""".format(campaignId)

        curs.execute(SQL)
        customerInCampaign = [customer[0] for customer in curs.fetchall()]
        # customerInSegment = [customer[0] for customer in customerInSegment]

        SQL = """SELECT OrderId, CustomerId, NetAmount, OrderTime
                 FROM foodfie.Order
                 where date(OrderTime) = current_date()"""

        curs.execute(SQL)
        orderDetail = curs.fetchall()
        todayCustomers = [order[1] for order in orderDetail]

        returnCustomers = list(set(customerInCampaign).intersection(todayCustomers))
        returnCustomerDetail = [order for order in orderDetail if order[1] in returnCustomers]
        if returnCustomerDetail:
            for customerDetail in returnCustomerDetail:
                orderId, customerId, orderAmount, orderTime = customerDetail

                SQL = """INSERT INTO foodfie_analysis.CampaignTracking(CampaignId, OrderId, CustomerId, OrderAmount, OrderTime)
                 VALUES({0}, {1}, {2}, {3}, '{4}')""".format(campaignId, orderId, customerId, orderAmount, orderTime)
                curs.execute(SQL)
                conn.commit()

trackCampaign()
