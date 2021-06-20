''' main/routes.py is the main flask routes page '''
from flask import render_template, Blueprint
from dailystockcount.models import Items, Invcount


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/report/", methods=['GET', 'POST'])
def report():
    ''' route for reports.html '''
    item_names = [item.itemname for item in Items.query.all()]
    inv_items = Invcount.query.all()
    ordered_items = Invcount.query.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).all()
    date_time = Invcount.query.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).first()

    return render_template('main/report.html', title='Variance-Daily', ordered_items=ordered_items,
                           inv_items=inv_items, item_names=item_names, date_time=date_time)
