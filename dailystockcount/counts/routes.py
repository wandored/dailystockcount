''' count/routes.py is flask routes for counts, purchases, sales and items. '''
from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from flask_login import current_user, login_required
from dailystockcount import db
from dailystockcount.models import Invcount, Purchases, Sales, Items
from dailystockcount.counts.utils import calculate_totals
from dailystockcount.counts.forms import (EnterCountForm, UpdateCountForm,
                                          EnterSalesForm, UpdateSalesForm,
                                          EnterPurchasesForm, UpdatePurchasesForm,
                                          NewItemForm, UpdateItemForm)

counts = Blueprint('counts', __name__)


@counts.route("/count/", methods=['GET', 'POST'])
@login_required
def count():
    ''' Enter count for an item '''
    page = request.args.get('page', 1, type=int)
    inv_items = Invcount.query.all()
    group_items = Invcount.query.group_by(
        Invcount.trans_date,
        Invcount.count_time)
    ordered_items = group_items.order_by(
        Invcount.trans_date.desc(),
        Invcount.count_time.desc()).paginate(
            page=page,
            per_page=10)
    form = EnterCountForm()
    if form.validate_on_submit():
        items_object = Items.query.filter_by(
            id=form.itemname.data.id).first()

        # Calculate the previous count
        filter_item = Invcount.query.filter(
            Invcount.itemname == form.itemname.data.itemname)
        previous_count = filter_item.order_by(
            Invcount.trans_date.desc()).first()
        if previous_count is None:
            total_previous = 0
        else:
            total_previous = previous_count.count_total

        # Calculate total purchases
        purchase_item = Purchases.query.filter_by(
            item_id=form.itemname.data.id,
            trans_date=form.transdate.data).first()
        if purchase_item is None:
            total_purchase = 0
        else:
            total_purchase = purchase_item.purchase_total

        # Calculate total sales
        sales_item = Sales.query.filter_by(
            item_id=form.itemname.data.id,
            trans_date=form.transdate.data).first()
        if sales_item is None:
            total_sales = 0
        else:
            total_sales = sales_item.sales_total

        date = form.transdate.data
        time = form.am_pm.data
        inventory = Invcount(
            trans_date=form.transdate.data,
            count_time=form.am_pm.data,
            itemname=form.itemname.data.itemname,
            casecount=form.casecount.data,
            eachcount=form.eachcount.data,
            count_total=(items_object.casepack *
                         form.casecount.data + form.eachcount.data),
            previous_total=total_previous,
            theory=(total_previous + total_purchase - total_sales),
            daily_variance=((items_object.casepack * form.casecount.data +
                             form.eachcount.data) -
                            (total_previous + total_purchase - total_sales)),
            item_id=form.itemname.data.id)
        db.session.add(inventory)
        db.session.commit()
        flash(
            f'Count submitted for {form.itemname.data.itemname} on {form.transdate.data}!', 'success')
        form.transdate.data = date
        form.am_pm.data = time
        return redirect(url_for('counts.count'))

    return render_template('counts/count.html', title='Enter Count', form=form,
                           inv_items=inv_items, ordered_items=ordered_items)


@counts.route("/count/<int:count_id>/update", methods=['GET', 'POST'])
@login_required
def update_count(count_id):
    ''' route for count/id/update '''
    item = Invcount.query.get_or_404(count_id)
    inv_items = Invcount.query.all()
    form = UpdateCountForm()
    if form.validate_on_submit():
        items_object = Items.query.filter_by(
            itemname=form.itemname.data).first()


'''
Need to find a way to identify item by id and not item name in "filter_item"
'''

        filter_item = Invcount.query.filter(
            Invcount.item_id == form.itemname.data,
            Invcount.trans_date <= form.transdate.data)
        ordered_count = filter_item.order_by(
            Invcount.trans_date.desc(), Invcount.count_time.desc()).offset(1).first()
        if ordered_count is None:
            total_previous = 0
        else:
            total_previous = ordered_count.count_total

        purchase_item = Purchases.query.filter_by(
            itemname=form.itemname.data, trans_date=form.transdate.data).first()
        if purchase_item is None:
            total_purchase = 0
        else:
            total_purchase = purchase_item.purchase_total

        sales_item = Sales.query.filter_by(
            itemname=form.itemname.data, trans_date=form.transdate.data).first()
        if sales_item is None:
            total_sales = 0
        else:
            total_sales = sales_item.sales_total

        item.trans_date = form.transdate.data
        item.count_time = form.am_pm.data
        item.itemname = form.itemname.data
        item.casecount = form.casecount.data
        item.eachcount = form.eachcount.data
        item.count_total = (items_object.casepack *
                            form.casecount.data + form.eachcount.data)
        item.previous_total = total_previous
        item.theory = (total_previous + total_purchase - total_sales)
        item.daily_variance = ((items_object.casepack * form.casecount.data +
                                form.eachcount.data) -
                               (total_previous + total_purchase - total_sales))
        db.session.commit()
        flash('Item counts have been updated!', 'success')
        return redirect(url_for('counts.count'))
    elif request.method == 'GET':
        form.transdate.data = item.trans_date
        form.am_pm.data = item.count_time
        form.itemname.data = item.itemname
        form.casecount.data = item.casecount
        form.eachcount.data = item.eachcount
    return render_template('counts/update_count.html',
                           title='Update Item Count',
                           form=form, inv_items=inv_items,
                           item=item, legend='Update Count')


@counts.route("/count/<int:count_id>/delete", methods=['POST'])
@login_required
def delete_count(count_id):
    ''' Delete an item count '''
    item = Invcount.query.get_or_404(count_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item counts have been deleted!', 'success')
    return redirect(url_for('counts.count'))


@counts.route("/purchases/", methods=['GET', 'POST'])
@login_required
def purchases():
    ''' Enter new purchases '''
    purchase_items = Purchases.query.all()
    inv_items = Items.query.all()
    item_number = Items.query.count()

    # Pagination
    page = request.args.get('page', 1, type=int)
    group_purchases = Purchases.query.group_by(Purchases.trans_date)
    ordered_purchases = group_purchases.order_by(
        Purchases.trans_date.desc()).paginate(page=page, per_page=10)

    form = EnterPurchasesForm()
    if form.validate_on_submit():
        items_object = Items.query.filter_by(
            id=form.itemname.data.id).first()
        purchase = Purchases(trans_date=form.transdate.data,
                             count_time='PM',
                             itemname=form.itemname.data.itemname,
                             casecount=form.casecount.data,
                             purchase_total=(
                                 items_object.casepack * form.casecount.data),
                             item_id=form.itemname.data.id)
        db.session.add(purchase)
        db.session.commit()
        flash(
            f'Purchases submitted for {form.itemname.data.itemname} on {form.transdate.data}!', 'success')
        calculate_totals(items_object.id)
        return redirect(url_for('counts.purchases'))
    return render_template('counts/purchases.html', title='Purchases',
                           form=form, purchase_items=purchase_items,
                           inv_items=inv_items,
                           ordered_purchases=ordered_purchases)


@counts.route("/purchases/<int:purchase_id>/update", methods=['GET', 'POST'])
@login_required
def update_purchases(purchase_id):
    item = Purchases.query.get_or_404(purchase_id)
    inv_items = Purchases.query.all()
    form = UpdatePurchasesForm()
    if form.validate_on_submit():
        items_object = Items.query.filter_by(
            itemname=form.itemname.data).first()
        item.trans_date = form.transdate.data
        item.itemname = form.itemname.data
        item.casecount = form.casecount.data
        item.purchase_total = (items_object.casepack * form.casecount.data)
        db.session.commit()
        flash('Item purchases have been updated!', 'success')
        calculate_totals(items_object.id)
        return redirect(url_for('counts.purchases'))
    elif request.method == 'GET':
        form.transdate.data = item.trans_date
        form.itemname.data = item.itemname
        form.casecount.data = item.casecount
    return render_template('counts/update_purchases.html',
                           title='Update Item Purchases',
                           form=form, inv_items=inv_items,
                           item=item, legend='Update Purchases')


@counts.route("/purchases/<int:purchase_id>/delete", methods=['POST'])
@login_required
def delete_purchases(purchase_id):
    item = Purchases.query.get_or_404(purchase_id)
    unit = Items.query.filter_by(
        itemname=item.itemname).first()
    db.session.delete(item)
    db.session.commit()
    flash('Item purchases have been deleted!', 'success')
    calculate_totals(unit.id)
    return redirect(url_for('counts.purchases'))


@counts.route("/sales/", methods=['GET', 'POST'])
@login_required
def sales():
    ''' Enter new sales for item '''
    page = request.args.get('page', 1, type=int)
    sales_items = Sales.query.all()
    group_sales = Sales.query.group_by(Sales.trans_date)
    ordered_sales = group_sales.order_by(
        Sales.trans_date.desc()).paginate(page=page, per_page=10)
    form = EnterSalesForm()
    if form.validate_on_submit():
        unit = Items.query.filter_by(
            id=form.itemname.data.id).first()
        sale = Sales(trans_date=form.transdate.data,
                     count_time='PM',
                     itemname=form.itemname.data.itemname,
                     eachcount=form.eachcount.data,
                     waste=form.waste.data,
                     sales_total=(form.eachcount.data + form.waste.data),
                     item_id=form.itemname.data.id)
        db.session.add(sale)
        db.session.commit()
        flash(
            f'Sales of {form.eachcount.data + form.waste.data} {form.itemname.data.itemname} submitted on {form.transdate.data}!', 'success')
        calculate_totals(unit.id)
        return redirect(url_for('counts.sales'))
    return render_template('counts/sales.html', title='Sales',
                           form=form, sales_items=sales_items,
                           ordered_sales=ordered_sales)


@counts.route("/sales/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_sales(item_id):
    ''' Update sales items '''
    item = Sales.query.get_or_404(item_id)
    inv_items = Sales.query.all()
    form = UpdateSalesForm()
    if form.validate_on_submit():
        unit = Items.query.filter_by(
            itemname=form.itemname.data).first()
        item.trans_date = form.transdate.data
        item.itemname = form.itemname.data
        item.eachcount = form.eachcount.data
        item.waste = form.waste.data
        item.sales_total = (form.eachcount.data + form.waste.data)
        db.session.commit()
        flash('Item Sales have been updated!', 'success')
        calculate_totals(unit.id)
        return redirect(url_for('counts.sales'))
    elif request.method == 'GET':
        form.transdate.data = item.trans_date
        form.itemname.data = item.itemname
        form.eachcount.data = item.eachcount
        form.waste.data = item.waste
    return render_template('counts/update_sales.html', title='Update Item Sales',
                           form=form, inv_items=inv_items,
                           item=item, legend='Update Sales')


@counts.route("/sales/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_sales(item_id):
    ''' Delete sales items '''
    item = Sales.query.get_or_404(item_id)
    unit = Items.query.filter_by(
        itemname=item.itemname).first()
    db.session.delete(item)
    db.session.commit()
    flash('Item Sales have been deleted!', 'success')
    calculate_totals(unit.id)
    return redirect(url_for('counts.sales'))


@counts.route("/item/new", methods=['GET', 'POST'])
@login_required
def new_item():
    ''' Create new inventory items '''
    inv_items = Items.query.all()
    form = NewItemForm()
    if form.validate_on_submit():
        item = Items(itemname=form.itemname.data,
                     casepack=form.casepack.data)
        db.session.add(item)
        db.session.commit()
        flash(f'New item created for {form.itemname.data}!', 'success')
        return redirect(url_for('counts.new_item'))
    return render_template('counts/new_item.html', title='New Inventory Item',
                           form=form, inv_items=inv_items,
                           legend='Enter New Item')


@counts.route("/item/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    ''' Update current inventory items '''
    item = Items.query.get_or_404(item_id)
    inv_items = Items.query.all()
    form = UpdateItemForm()
    if form.validate_on_submit():
        item.itemname = form.itemname.data
        item.casepack = form.casepack.data
        db.session.commit()
        flash(f'{item.itemname} has been updated!', 'success')
        return redirect(url_for('counts.new_item'))
    elif request.method == 'GET':
        form.itemname.data = item.itemname
        form.casepack.data = item.casepack
    return render_template('counts/update_item.html',
                           title='Update Inventory Item',
                           form=form, inv_items=inv_items,
                           item=item, legend='Update Case Pack for ')


@counts.route("/item/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_item(item_id):
    ''' Delete current items '''
    item = Items.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Product has been 86'd!", 'success')
    return redirect(url_for('counts.new_item'))
