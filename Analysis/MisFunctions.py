import os
import sys
import logging
import random
import datetime

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


def getProductData(customerId):

    SQL = """select d.CategoryName, c.ItemName, d.CategoryId
            from foodfie.Order a
            join foodfie.OrderDetail b
            on a.OrderId = b.OrderId
            and a.CustomerId = {}
            join foodfie.Item c
            on b.ItemId = c.ItemId
            join foodfie.Category d
            on c.CategoryId = d.CategoryId;
            """.format(customerId)

    curs.execute(SQL)
    productData = curs.fetchall()
    whatEat = []
    whatMoreCanEat = []
    for item in productData:
        whatEat.append(item[0] + '-' + item[1])

        SQL = """select distinct concat(CategoryName, "-", ItemName)
                from foodfie.Category a
                join foodfie.Item b
                on a.CategoryId = b.CategoryId
                and a.CategoryId in ({})""".format(item[2])

        curs.execute(SQL)
        moreOptionAvble = curs.fetchall()
        for it in moreOptionAvble:
            whatMoreCanEat.append(it[0])

    if len(whatEat):
        random.shuffle(whatEat)
        whatEat = random.choice(whatEat)
    if len(whatMoreCanEat):
        random.shuffle(whatMoreCanEat)
        whatMoreCanEat = random.choice(whatMoreCanEat)
    return [str(whatEat), str(whatMoreCanEat)]


def lostCustomers(customerId):

    todayDate = datetime.datetime.today().date()
    while todayDate.weekday() != 5:
        todayDate += datetime.timedelta(1)

    couponCode = 'ff' + str(random.randint(1111, 9999))
    upcomingSaturday = todayDate
    # insert coupon in Coupon code table
    SQL = """INSERT INTO foodfie.CouponCode(CustomerId, CouponCodeName, CouponCodeDiscount, CouponCodeValidTill)
             VALUES({0}, '{1}', 20, '{2}')""".format(customerId, couponCode, upcomingSaturday)
    curs.execute(SQL)
    conn.commit()

    return [couponCode, upcomingSaturday]


