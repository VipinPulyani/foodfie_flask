from flask_cors import CORS, cross_origin
from flask import Blueprint, request, Response, jsonify
from Misc.foodfie_db.db import connectDB
import config

coupon_API = Blueprint('coupon_api', __name__)
CORS(coupon_API)


@coupon_API.route('/api/v1.0/verifycoupon', methods = ['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def verifyCoupon():

    customerId = request.args.get('customerid')
    couponCode = request.args.get('coupon')
    totalAmount = int(request.args.get('totalamount'))

    conn, cur = connectDB()
    cur.execute("""select CouponCodeName
                    from foodfie.CouponCode
                    where lower(couponcodename) = lower('{0}')
                """.format(couponCode))

    validCoupon = cur.fetchall()

    if validCoupon:
        cur.execute("""select * 
                        from foodfie.CouponCode
                        where lower(couponcodename) = lower('{0}')
                        and CouponCodeValidTill >= current_date()""".format(validCoupon[0][0]))
        validDate = cur.fetchall()

        if validDate:

            cur.execute("""select CouponCodeMaximumValue, CouponCodeDiscount, CouponCodeRedeem, MinimumAmount
                           from foodfie.CouponCode
                           where lower(CouponCodeName) = lower('{0}')
                           and CustomerId = {1}""".format(couponCode, customerId))
            couponWithCustomer = cur.fetchall()

            if couponWithCustomer:
                maximumDiscount = couponWithCustomer[0][0]
                discountPercentage = couponWithCustomer[0][1]
                isRedeem = couponWithCustomer[0][2]
                minimumamount = couponWithCustomer[0][3]

                if totalAmount >= minimumamount:
                    if isRedeem == 0:
                        discount = round((totalAmount * discountPercentage)/100)
                        if maximumDiscount > discount:
                            return jsonify({'isCouponValid': 1, 'discount': discount})
                        else:
                            return jsonify({'isCouponValid': 1, 'discount': maximumDiscount})
                    else:
                        return jsonify({'isCouponValid': 0, 'issue': 'Already redeemed'})
                else:
                    return jsonify({'isCouponValid': 0, 'issue': 'Minimum Amount Required: {0}'.format(minimumamount)})
            else:
                cur.execute("""select CouponCodeMaximumValue, CouponCodeDiscount, 
                            CouponNoOfRedeems, MinimumAmount
                           from foodfie.CouponCode
                           where lower(CouponCodeName) = lower('{0}')
                           and (CustomerId is Null or customerid = 0)""".format(couponCode))
                couponWithoutCustomer = cur.fetchall()
                if couponWithoutCustomer:
                    maximumDiscount = couponWithoutCustomer[0][0]
                    discountPercentage = couponWithoutCustomer[0][1]
                    noRedeem = couponWithoutCustomer[0][2]
                    minimumamount = couponWithoutCustomer[0][3]

                    if totalAmount >= minimumamount:
                        if noRedeem > 0:
                            discount = round((totalAmount * discountPercentage)/100)
                            if maximumDiscount > discount:
                                return jsonify({'isCouponValid': 1, 'discount': discount})
                            else:
                                return jsonify({'isCouponValid': 1, 'discount': maximumDiscount})
                        else:
                            return jsonify({'isCouponValid': 0, 'issue': 'Already redeemed'})
                    else:
                        return jsonify({'isCouponValid': 0, 'issue': 'Minimum Amount Required: {0}'.format(minimumamount)})
                else:
                    return jsonify({'isCouponValid': 0, 'issue': 'Not valid for this customer'})

        else:
            cur.execute("""select CouponCodeValidTill
                           from foodfie.CouponCode
                           where lower(CouponCodeName) = lower('{0}')
                           and CustomerId = {1}""".format(couponCode, customerId))
            validTill = cur.fetchall()

            if validTill:
                return jsonify({'isCouponValid': 0, 'issue': 'Coupon Code is valid till {0}'.format(validTill[0][0])})
            else:
                cur.execute("""select CouponCodeValidTill
                            from foodfie.CouponCode
                            where lower(CouponCodeName) = lower('{0}')
                            and (CustomerId is Null or customerid = 0)""".format(validCoupon[0][0]))
                validTill = cur.fetchall()
                if validTill:
                    return jsonify({'isCouponValid': 0, 'issue': 'Coupon Code is valid till {0}'.format(validTill[0][0])})
                else:
                    return jsonify({'isCouponValid': 0, 'issue': 'Not valid for this customer'})
    else:
        return jsonify({'isCouponValid': 0, 'issue': 'Not a valid coupon'})


def redeemcoupon(customerId, couponCode):

    SQL = """SELECT CouponCodeId, CouponCodeRedeem 
             FROM foodfie.CouponCode
             WHERE customerid = {0}
             AND couponcodename = '{1}'""".format(customerId, couponCode)

    conn, curs = connectDB()
    curs.execute(SQL)

    individualCoupon = curs.fetchall()

    if individualCoupon:
        SQL = """UPDATE foodfie.CouponCode
                 SET CouponCodeRedeem = 1
                 WHERE customerid = {0}
                 AND couponcodename = '{1}'""".format(customerId, couponCode)

        curs.execute(SQL)
        conn.commit()

    else:

        SQL = """SELECT CouponCodeId, CouponNoOfRedeems 
                 FROM foodfie.CouponCode
                 WHERE (CustomerId is Null or customerid = 0)
                 AND couponcodename = '{0}'""".format(couponCode)

        curs.execute(SQL)
        groupCoupon = curs.fetchall()[0]
        if groupCoupon:
            cId, cRedeem = groupCoupon

            SQL = """UPDATE foodfie.CouponCode
                 SET CouponNoOfRedeems = {0} - 1
                 WHERE CouponCodeId = {1}""".format(cRedeem, cId)

            curs.execute(SQL)
            conn.commit()


