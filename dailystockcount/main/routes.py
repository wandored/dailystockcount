''' main/routes.py is the main flask routes page '''
from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required
from sqlalchemy import or_, and_, func
from dailystockcount import db
from dailystockcount.models import Items, Invcount, Sales, Purchases
from datetime import datetime, timedelta, date


main = Blueprint('main', __name__)


@main.route("/home/")
def home():
    return render_template('main/home.html', title='Home')


@main.route("/")
@main.route("/report/", methods=['GET', 'POST'])
@login_required
def report():
    ''' route for reports.html '''
    ordered_counts = Invcount.query.order_by(
        Invcount.trans_date.desc(),
        Invcount.count_time.desc(),
        Invcount.daily_variance).all()
    date_time = Invcount.query.order_by(
        Invcount.trans_date.desc(),
        Invcount.count_time.desc()).first()

    if not ordered_counts:
        return redirect(url_for('counts.new_item'))

    return render_template('main/report.html',
                           title='Variance-Daily',
                           ordered_counts=ordered_counts,
                           date_time=date_time)


@main.route("/report/<item_name>/details", methods=['GET', 'POST'])
@login_required
def report_details(item_name):
    ''' display item details '''
    # restrict results to the last 7 & 28 days
    last_count = Invcount.query.order_by(Invcount.trans_date.desc()).first()
    end_date = last_count.trans_date
    weekly = end_date - timedelta(days=6)
    monthly = end_date - timedelta(days=27)

    # Boxex Calculations
    count_daily = db.session.query(Invcount
                                   ).filter(Invcount.itemname == item_name,
                                            Invcount.count_time == "PM",
                                            Invcount.trans_date == end_date).first()
    sales_weekly = db.session.query(Sales,
                                    func.sum(Sales.eachcount).label('total'),
                                    func.avg(Sales.eachcount).label(
                                        'sales_avg')
                                    ).filter(Sales.itemname == item_name,
                                             Sales.count_time == "PM",
                                             Sales.trans_date >= weekly).all()
    purchase_weekly = db.session.query(Purchases,
                                       func.sum(Purchases.purchase_total).label(
                                           'total')
                                       ).filter(Purchases.itemname == item_name,
                                                Purchases.count_time == "PM",
                                                Purchases.trans_date >= weekly).all()
    on_hand_weekly = db.session.query(Invcount,
                                      func.avg(Invcount.count_total).label(
                                          'average')
                                      ).filter(Invcount.itemname == item_name,
                                               Invcount.trans_date >= weekly).all()

#    def get_daily_values(day):
#        day_of_week = Sales.query.order_by(Sales.trans_date.desc()).first()
#        day_sales = db.session.query(Sales,
#                                     func.avg(Sales.eachcount).label('average')
#                                     ).filter(Sales.itemname == item_name,
#                                              Sales.trans_date == monthly,
#                                              Sales.trans_date.weekday() == day).all()
#        return day_sales.average
#
#    daily_values = []
#    days = [2, 3, 4, 5, 6, 0, 1]
#    for day in days:
#        daily_values.append(get_daily_values(day))

    # Charts
    items_list = db.session.query(Invcount
                                  ).filter(Invcount.itemname == item_name,
                                           Invcount.count_time == "PM",
                                           Invcount.trans_date >= weekly
                                           ).order_by(Invcount.trans_date).all()
    labels = []
    values = []
    for i in items_list:
        labels.append(i.trans_date.strftime('%A'))
        values.append(i.count_total)

    sales_list = db.session.query(Sales).filter(
        Sales.itemname == item_name, Sales.trans_date >= weekly).order_by(Sales.trans_date).all()
    day_sales = []
    for i in sales_list:
        day_sales.append(i.sales_total)

    # Weekly Details Table
    result = db.session.query(Invcount,
                              func.sum(Sales.eachcount).label('sales_count'),
                              func.sum(Sales.waste).label('sales_waste'),
                              func.sum(Purchases.purchase_total).label(
                                  'purchase_count')
                              ).select_from(Invcount). \
        outerjoin(Sales, and_(Sales.trans_date == Invcount.trans_date,
                              Sales.itemname == item_name)). \
        outerjoin(Purchases, and_(Purchases.trans_date == Invcount.trans_date,
                                  Purchases.itemname == item_name)). \
        group_by(Invcount.itemname,
                 Invcount.trans_date). \
        order_by(Invcount.trans_date.desc()). \
        filter(Invcount.itemname == item_name,
               Invcount.count_time ==
               "PM", Invcount.trans_date >= weekly)

    return render_template('main/details.html',
                           title='Item Variance Details',
                           count_daily=count_daily,
                           sales_weekly=sales_weekly,
                           purchase_weekly=purchase_weekly,
                           on_hand_weekly=on_hand_weekly,
                           item_name=item_name,
                           labels=labels,
                           values=values,
                           day_sales=day_sales,
                           result=result)
