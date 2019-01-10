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
    from SMS.SMS_Misc import randomCampaignSMS
    from Analysis import MisFunctions
    from Analysis.CustomerSegmentation import updateCustomerSegement

logg = logging.getLogger(__name__)
logg = logger.setLogger(logg)

conn, curs = connectDB()


def runCampaign(campaignId):
    """
    Run campaign and send SMS
    :param campaignId: Campaign Id
    :return:
    """
    logg.info("=>Running Campaign")
    # Get Campaign Detail
    SQL = """SELECT a.CampaignId, a.CampaignName, a.CustomerSegmentId, a.CampaignMessageTypeId,
                    b.CustomerSegmentName
            FROM foodfie_analysis.Campaign a
            JOIN foodfie_analysis.CustomerSegments b
            ON a.CustomerSegmentId = b.CustomerSegmentId 
            AND a.CampaignId  = {0}""".format(campaignId)

    curs.execute(SQL)
    campaignDetail = curs.fetchall()

    campaignId, campaignName, customerSegmentId, campaignMessageTypeId, segmentName = campaignDetail[0]
    logg.info("""CampaignId: {0},
                 CampaignName: {1}, 
                 CustomerSegmentId: {2},
                 CampaignMessage: {3},
                 SegmentName: {4}"""
                .format(campaignId, campaignName, customerSegmentId, campaignMessageTypeId, segmentName))

    logg.info("=>Finding Customer Segement")
    logg.info("SegementId: {0}".format(customerSegmentId))

    SQL = """Select CustomerSegmentId, SQLQuery
             from foodfie_analysis.CustomerSegments
             where CustomerSegmentId = {}""".format(customerSegmentId)
    curs.execute(SQL)
    logg.info("SQL Query: {}".format(SQL))
    segmentDetail = curs.fetchall()

    customerSegId, SQL = segmentDetail[0]

    curs.execute(SQL)
    customerInSegment = curs.fetchall()

    logg.info("Total Customers: {}".format(customerInSegment.__len__()))
    logg.info("Inserting into CustomerSegmentSummary")
    # Insert total rows in SegmentSummary table
    SQL = """insert into foodfie_analysis.CustomerSegmentsSummary(CustomerSegmentsId, TotalCustomer)
             values({0}, {1})""".format(customerSegId, segmentDetail.__len__())
    curs.execute(SQL)
    conn.commit()

    #updateCustomerSegement(customerSegmentId)
    logg.info("..done")

    # Get Campaign Message Type
    SQL = """SELECT needtoreplace, replacewith
             FROM foodfie_analysis.CampaignMessageType
             WHERE campaignmessagetypeid = {}""".format(campaignMessageTypeId)
    curs.execute(SQL)
    needToReplace, replaceFuncName = curs.fetchall()[0]
    needToReplace = needToReplace.split(',') if needToReplace else ''
    logg.info("=>Sending SMS")
    for customer in customerInSegment:
        replaceWith = getattr(MisFunctions, replaceFuncName)(customer[0]) if replaceFuncName else ''
        logg.info("Sending SMS to CustomerId:{0} and campaignMessageTypeId:{1}".format(customer[0], campaignMessageTypeId))
        randomCampaignSMS(customer[0], campaignId, campaignMessageTypeId, needToReplace, replaceWith)


if __name__ == "__main__":
    campaignId = sys.argv[1]
    runCampaign(campaignId)

# Customer Segement - Lost Customer - 20% discount - Time bound
# Customer Segement - Inventory Left - Flash Sales - 3 Hours
# Customer Segment - Saturday - Reminder
# Customer Segement - Repeat Customer - Reminder - Try something else
# Customer Segement -


