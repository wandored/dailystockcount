''' main/routes.py is the main flask routes page '''
from flask import render_template, Blueprint
from flask_login import login_required
from sqlalchemy import or_
from dailystockcount import db
from dailystockcount.models import Items, Invcount, Sales, Purchases


main = Blueprint('main', __name__)


@main.route("/home/")
def home():
    return render_template('main/home.html', title='Home')


@main.route("/")
@main.route("/report/", methods=['GET', 'POST'])
@login_required
def report():
    ''' route for reports.html '''
    item_names = [item.itemname for item in Items.query.all()]
    inv_items = Invcount.query.all()
    ordered_items = Invcount.query.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc(), Invcount.daily_variance).all()
    date_time = Invcount.query.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).first()

    return render_template('main/report.html', title='Variance-Daily',
                           ordered_items=ordered_items,
                           inv_items=inv_items,
                           item_names=item_names,
                           date_time=date_time)


@main.route("/report/<item_name>/details", methods=['GET', 'POST'])
@login_required
def report_details(item_name):
    ''' display item details '''
    items_list = Invcount.query.filter(Invcount.itemname == item_name).order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).limit(7)
    sales_list = Sales.query.filter(Sales.itemname == item_name).order_by(
        Sales.trans_date.desc(), Sales.count_time.desc()).limit(7)
    purchase_list = Purchases.query.filter(Purchases.itemname == item_name).order_by(
        Purchases.trans_date.desc(), Purchases.count_time.desc()).limit(7)

    result = db.session.query(Invcount, Purchases, Sales).select_from(Invcount).filter(Invcount.itemname == item_name). \
        outerjoin(Purchases, Purchases.trans_date == Invcount.trans_date).filter(or_(Purchases.itemname == item_name, Purchases.itemname == None)). \
        outerjoin(Sales, Sales.trans_date == Invcount.trans_date).filter(or_(Sales.itemname == item_name, Sales.itemname == None)). \
        order_by(Invcount.trans_date.desc()).limit(7)

    return render_template('main/details.html', title='Item Variance Details',
                           items_list=items_list,
                           sales_list=sales_list,
                           purchase_list=purchase_list,
                           item_name=item_name,
                           result=result)
