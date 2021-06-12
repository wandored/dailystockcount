from flask import render_template, request, Blueprint
from dailycount.models import Invcount


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/report/")
def report():
    inv_items = Invcount.query.all()
    group_items = Invcount.query.group_by(Invcount.trans_date)
    ordered_group = group_items.order_by(Invcount.trans_date.desc())
    return render_template('report.html', title='Reports', inv_items=inv_items, group_items=group_items, ordered_group=ordered_group)
