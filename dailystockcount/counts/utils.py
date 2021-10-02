''' Calculation functions '''
from flask import flash
from dailystockcount import db
from dailystockcount.models import Invcount, Purchases, Sales, Items


def calculate_totals(item_id):
    ''' Run the variance calculations for each item '''
    unit = Items.query.get_or_404(item_id)
    filter_item = Invcount.query.filter(
        Invcount.item_id == unit.id)
    ordered_count = filter_item.order_by(
        Invcount.trans_date.desc(), Invcount.count_time.desc()).first()

    if ordered_count is not None:
        purchase_item = Purchases.query.filter_by(
            item_id=unit.id, trans_date=ordered_count.trans_date).first()
        if purchase_item is None:
            total_purchase = 0
        else:
            total_purchase = purchase_item.purchase_total

        sales_item = Sales.query.filter_by(
            item_id=unit.id, trans_date=ordered_count.trans_date).first()
        if sales_item is None:
            total_sales = 0
        else:
            total_sales = sales_item.sales_total

        ordered_count.theory = (ordered_count.previous_total +
                                total_purchase - total_sales)
        ordered_count.daily_variance = ((unit.casepack * ordered_count.casecount +
                                         ordered_count.eachcount) -
                                        (ordered_count.previous_total +
                                         total_purchase - total_sales))
        db.session.commit()
        flash('Variances have been recalculated!', 'success')
