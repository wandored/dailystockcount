''' main/routes.py is the main flask routes page '''
from datetime import timedelta
from flask import render_template, Blueprint, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import and_, func
from dailystockcount import db
from dailystockcount.models import Invcount, Sales, Purchases, Items


main = Blueprint('main', __name__)


@main.route("/home/")
def home():
    return render_template('main/home.html', title='Home')


@main.route("/")
@main.route("/report/", methods=['GET', 'POST'])
@login_required
def report():
    ''' route for reports.html '''
    is_items = Items.query.first()
    if not is_items:
        flash('The first step is to add the items you want to count!', 'warning')
        return redirect(url_for('counts.new_item'))
    ordered_counts = Invcount.query.order_by(
        Invcount.trans_date.desc(),
        Invcount.count_time.desc(),
        Invcount.daily_variance).all()
    date_time = Invcount.query.order_by(
        Invcount.trans_date.desc(),
        Invcount.count_time.desc()).first()

    if not ordered_counts:
        flash('You must first enter Counts to see Reports!', 'warning')
        return redirect(url_for('counts.count'))

    return render_template('main/report.html',
                           title='Variance-Daily',
                           ordered_counts=ordered_counts,
                           date_time=date_time)


@main.route("/report/<product>/details", methods=['GET', 'POST'])
@login_required
def report_details(product):
    ''' display item details '''
    # restrict results to the last 7 & 28 days
    last_count = Invcount.query.order_by(Invcount.trans_date.desc()).first()
    end_date = last_count.trans_date
    weekly = end_date - timedelta(days=6)
    monthly = end_date - timedelta(days=27)

    # Boxes Calculations
    count_daily = db.session.query(Invcount
                                   ).filter(Invcount.item_id == product,
                                            Invcount.count_time == "PM",
                                            Invcount.trans_date == end_date).first()
    sales_weekly = db.session.query(Sales,
                                    func.sum(Sales.eachcount).label('total'),
                                    func.avg(Sales.eachcount).label(
                                        'sales_avg')
                                    ).filter(Sales.item_id == product,
                                             Sales.count_time == "PM",
                                             Sales.trans_date >= weekly).all()
    purchase_weekly = db.session.query(Purchases,
                                       func.sum(Purchases.purchase_total).label(
                                           'total')
                                       ).filter(Purchases.item_id == product,
                                                Purchases.count_time == "PM",
                                                Purchases.trans_date >= weekly).all()
    on_hand_weekly = db.session.query(Invcount,
                                      func.avg(Invcount.count_total).label(
                                          'average')
                                      ).filter(Invcount.item_id == product,
                                               Invcount.trans_date >= weekly).all()

    # Chart 1
    items_list = db.session.query(Invcount
                                  ).filter(Invcount.item_id == product,
                                           Invcount.count_time == "PM",
                                           Invcount.trans_date >= weekly
                                           ).order_by(Invcount.trans_date).all()
    labels = []
    values = []
    day_sales = []
    for i in items_list:
        labels.append(i.trans_date.strftime('%A'))
        values.append(i.count_total)
        sales_list = db.session.query(Sales).filter(
            Sales.item_id == product,
            Sales.trans_date == i.trans_date).first()
        if sales_list:
            day_sales.append(sales_list.sales_total)
        else:
            day_sales.append(0)

    # Chart #2
    daily_sales = db.session.query(func.extract("dow", Sales.trans_date).label('dow'),
                                   func.avg(Sales.eachcount).label('average')
                                   ).filter(Sales.item_id == product,
                                            Sales.trans_date >= monthly).group_by(
                                                func.extract("dow", Sales.trans_date)).all()

    weekly_avg = db.session.query(Sales,
                                  func.avg(Sales.eachcount).label('sales_avg'),
                                  func.avg(Sales.waste).label('waste_avg')
                                  ).filter(Sales.item_id == product,
                                           Sales.trans_date >= monthly)

    values2 = []
    values3 = []
    values4 = []
    for d in daily_sales:
        values2.append(d.average)
        for w in weekly_avg:
            values3.append(w.sales_avg)
            values4.append(w.waste_avg)

    # Details Table
    result = db.session.query(Invcount,
                              func.sum(Sales.eachcount).label('sales_count'),
                              func.sum(Sales.waste).label('sales_waste'),
                              func.sum(Purchases.purchase_total).label(
                                  'purchase_count')
                              ).select_from(Invcount). \
        outerjoin(Sales, and_(Sales.trans_date == Invcount.trans_date,
                              Sales.item_id == product)). \
        outerjoin(Purchases, and_(Purchases.trans_date == Invcount.trans_date,
                                  Purchases.item_id == product)). \
        group_by(Invcount.item_id,
                 Invcount.trans_date). \
        order_by(Invcount.trans_date.desc()). \
        filter(Invcount.item_id == product,
               Invcount.count_time ==
               "PM", Invcount.trans_date >= weekly)

    item_name = db.session.query(Items
                                 ).filter(Items.id == product).first()

    return render_template('main/details.html',
                           title='Item Variance Details',
                           count_daily=count_daily,
                           sales_weekly=sales_weekly,
                           purchase_weekly=purchase_weekly,
                           on_hand_weekly=on_hand_weekly,
                           item_name=item_name,
                           labels=labels,
                           labels2=labels,
                           values=values,
                           values2=values2,
                           values3=values3,
                           values4=values4,
                           day_sales=day_sales,
                           daily_sales=daily_sales,
                           result=result)
