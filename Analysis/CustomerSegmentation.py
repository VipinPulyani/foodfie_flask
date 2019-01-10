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


def updateCustomerSegement(segementId):
    logg.info("=>Customer Segementaion")
    logg.info("SegementId: {0}".format(segementId))

    SQL = """Select CustomerSegmentId, SQLQuery
             from foodfie_analysis.CustomerSegments
             where CustomerSegmentId = {}""".format(segementId)

    curs.execute(SQL)
    allSegments = curs.fetchall()

    logg.info("SQL Query: {}".format(SQL))
    for segment in allSegments:
        customerSegId = segment[0]
        SQL = segment[1]
        curs.execute(SQL)
        segmentDetail = curs.fetchall()

        logg.info("Total Customers: {}".format(segmentDetail.__len__()))
        logg.info("Inserting into CustomerSegmentSummary")
        # Insert total rows in SegmentSummary table
        SQL = """insert into foodfie_analysis.CustomerSegmentsSummary(CustomerSegmentsId, TotalCustomer)
                 values({0}, {1})""".format(customerSegId, segmentDetail.__len__())
        curs.execute(SQL)
        conn.commit()

        return
        # # Delete all the rows if already available
        # SQL = """SET SQL_SAFE_UPDATES = 0"""
        # curs.execute(SQL)
        #
        # SQL = """delete from foodfie_analysis.CustomerSegmentsDetail
        #          where CustomerSegmentsId = {0}""".format(customerSegId)
        # curs.execute(SQL)
        # conn.commit()
        # logg.info("Deleting from CustomerSegmentsDetail: {}".format(SQL))
        # SQL = """SET SQL_SAFE_UPDATES = 1"""
        # curs.execute(SQL)
        # logg.info("Insertin into CustomerSegmentDetail")
        # for customer in segmentDetail:
        #     logg.info("CustomerSegmentId: {0}, CustomerId: {1}".format(customerSegId,customer[0]))
        #     SQL = """insert into foodfie_analysis.CustomerSegmentsDetail(CustomerSegmentsId, CustomerId,CustomerPhoneNo)
        #              values({0},{1},{2})""".format(customerSegId, customer[0], customer[1])
        #     curs.execute(SQL)
        #     conn.commit()


