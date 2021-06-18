import sqlite3
import pandas as pd
from flask import render_template, Blueprint
from sqlalchemy import create_engine
from dailycount import db
from dailycount.models import Totals, Items, Invcount, Purchases, Sales


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/report/", methods=['GET', 'POST'])
def report():
    item_names = [item.itemname for item in Items.query.all()]
    inv_items = Invcount.query.all()
    ordered_items = Invcount.query.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).all()
    date_time = Invcount.query.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).first()

    return render_template('report.html', title='Variance-Daily', ordered_items=ordered_items,
                           inv_items=inv_items, item_names=item_names,
                           date_time=date_time)
