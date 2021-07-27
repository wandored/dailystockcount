''' main/routes.py is the main flask routes page '''
from flask import render_template, Blueprint
from flask_login import login_required
from sqlalchemy import or_, and_, func
from dailystockcount import db
from dailystockcount.models import Items, Invcount, Sales, Purchases
from datetime import datetime, timedelta


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

    # Calculate Weekly Averages
    wkly_on_hand = db.session.query(Invcount, func.avg(Invcount.count_total).label(
        'average')).filter(Invcount.itemname == item_name, Invcount.trans_date >= weekly).all()
    wkly_variance = db.session.query(Invcount, func.avg(Invcount.daily_variance).label('variance')).filter(
        Invcount.itemname == item_name, Invcount.trans_date >= weekly).all()
    wkly_sales = db.session.query(Sales, func.avg(Sales.eachcount).label('average'), func.avg(Sales.waste).label('waste')).filter(
        Sales.itemname == item_name, Sales.trans_date >= weekly).all()

    # Calculate Monthly Averages
    mon_avg_on_hand = db.session.query(Invcount, func.avg(Invcount.count_total).label(
        'average')).filter(Invcount.itemname == item_name, Invcount.trans_date >= monthly).all()
    mon_avg_variance = db.session.query(Invcount, func.avg(Invcount.daily_variance).label('variance')).filter(
        Invcount.itemname == item_name, Invcount.trans_date >= monthly).all()
    mon_avg_sales = db.session.query(Sales, func.avg(Sales.eachcount).label('average'), func.avg(Sales.waste).label('waste')).filter(
        Sales.itemname == item_name, Sales.trans_date >= monthly).all()

    # Calculate Weekly Totals
    total_variance = db.session.query(Invcount, func.sum(Invcount.daily_variance).label('variance')).filter(
        Invcount.itemname == item_name, Invcount.trans_date >= weekly).all()
    sales_wk = db.session.query(Sales, func.sum(Sales.eachcount).label('weekly_sales'), func.sum(Sales.waste).label('weekly_waste')).filter(
        Sales.itemname == item_name, Sales.trans_date >= weekly).all()
    wkly_tot_purchase = db.session.query(Purchases, func.sum(Purchases.purchase_total).label('purchases')).filter(
        Purchases.itemname == item_name, Purchases.trans_date >= weekly).all()

    # Charts
    items_list = db.session.query(Invcount).filter(Invcount.itemname == item_name,
                                                   Invcount.count_time == "PM",
                                                   Invcount.trans_date >= weekly).order_by(Invcount.trans_date).all()
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
    result = db.session.query(Invcount, Sales, Purchases).select_from(Invcount). \
        filter(and_(Invcount.itemname == item_name, Invcount.count_time == "PM", Invcount.trans_date >= weekly)). \
        outerjoin(Sales, Sales.trans_date == Invcount.trans_date). \
        filter(or_(Sales.itemname == item_name, Sales.itemname == None)). \
        outerjoin(Purchases, Purchases.trans_date == Invcount.trans_date). \
        filter(or_(Purchases.itemname == item_name, Purchases.itemname == None)). \
        order_by(Invcount.trans_date.desc()).all()

    return render_template('main/details.html',
                           title='Item Variance Details',
                           wkly_on_hand=wkly_on_hand,
                           sales_wk=sales_wk,
                           wkly_sales=wkly_sales,
                           total_variance=total_variance,
                           wkly_variance=wkly_variance,
                           wkly_tot_purchase=wkly_tot_purchase,
                           mon_avg_sales=mon_avg_sales,
                           mon_avg_variance=mon_avg_variance,
                           mon_avg_on_hand=mon_avg_on_hand,
                           item_name=item_name,
                           items_list=items_list,
                           labels=labels,
                           values=values,
                           day_sales=day_sales,
                           result=result)
