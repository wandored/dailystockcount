''' main/routes.py is the main flask routes page '''
from flask import render_template, Blueprint
from dailystockcount.models import Items, Invcount


main = Blueprint('main', __name__)


@main.route("/home/")
def home():
    return render_template('main/home.html', title='Home')


@main.route("/")
@main.route("/report/", methods=['GET', 'POST'])
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
def report_details(item_name):
    ''' display item details '''
    items_list = Invcount.query.filter(Invcount.itemname == item_name)
    ordered_items = items_list.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).all()

    return render_template('main/details.html', title='Item Variance Details',
                           ordered_items=ordered_items,
                           items_list=items_list)
