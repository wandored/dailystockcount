from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from dailycount import db
from dailycount.models import Invcount, Purchases, Sales, Items
from dailycount.counts.forms import (EnterCountForm, UpdateCountForm, EnterSalesForm,
                                     UpdateSalesForm, EnterPurchasesForm, UpdatePurchasesForm, NewItemForm)

counts = Blueprint('counts', __name__)


@counts.route("/count/", methods=['GET', 'POST'])
@login_required
def count():
    page = request.args.get('page', 1, type=int)
    inv_items = Invcount.query.all()
    group_items = Invcount.query.group_by(
        Invcount.trans_date, Invcount.count_time)
    ordered_items = group_items.order_by(
        Invcount.trans_date.desc()).paginate(page=page, per_page=10)
    form = EnterCountForm()
    if form.validate_on_submit():
        inventory = Invcount(trans_date=form.transdate.data, count_time=form.am_pm.data, itemname=form.itemname.data.itemname,
                             casecount=form.casecount.data, eachcount=form.eachcount.data, manager=current_user)
        db.session.add(inventory)
        db.session.commit()
        flash(
            f'Count submitted for {form.itemname.data.itemname} on {form.transdate.data}!', 'success')
        return redirect(url_for('counts.count'))
    return render_template('count.html', title='Enter Count', form=form, inv_items=inv_items, group_items=group_items, ordered_items=ordered_items)


@counts.route("/count/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_count(item_id):
    item = Invcount.query.get_or_404(item_id)
    inv_items = Invcount.query.all()
    form = UpdateCountForm()
    if form.validate_on_submit():
        item.trans_date = form.transdate.data
        item.count_time = form.am_pm.data
        item.itemname = form.itemname.data
        item.casecount = form.casecount.data
        item.eachcount = form.eachcount.data
        db.session.commit()
        flash('Item counts have been updated!', 'success')
        return redirect(url_for('counts.count'))
    elif request.method == 'GET':
        form.transdate.data = item.trans_date
        form.am_pm.data = item.count_time
        form.itemname.data = item.itemname
        form.casecount.data = item.casecount
        form.eachcount.data = item.eachcount
    return render_template('update_count.html', title='Update Item Count', form=form, inv_items=inv_items, item=item, legend='Update Count')


@counts.route("/count/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_count(item_id):
    item = Invcount.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item counts have been deleted!', 'success')
    return redirect(url_for('counts.count'))


@counts.route("/purchases/", methods=['GET', 'POST'])
@login_required
def purchases():
    page = request.args.get('page', 1, type=int)
    purchase_items = Purchases.query.all()
    group_purchases = Purchases.query.group_by(Purchases.trans_date)
    ordered_purchases = group_purchases.order_by(
        Purchases.trans_date.desc()).paginate(page=page, per_page=10)
    form = EnterPurchasesForm()
    if form.validate_on_submit():
        purchas = Purchases(trans_date=form.transdate.data,
                            itemname=form.itemname.data.itemname, casecount=form.casecount.data)
        db.session.add(purchas)
        db.session.commit()
        flash(
            f'Purchases submitted for {form.itemname.data.itemname} on {form.transdate.data}!', 'success')
        return redirect(url_for('counts.purchases'))
    return render_template('purchases.html', title='Purchases', form=form, purchase_items=purchase_items, ordered_purchases=ordered_purchases)


@counts.route("/purchases/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_purchases(item_id):
    item = Purchases.query.get_or_404(item_id)
    inv_items = Purchases.query.all()
    form = UpdatePurchasesForm()
    if form.validate_on_submit():
        item.trans_date = form.transdate.data
        item.itemname = form.itemname.data
        item.casecount = form.casecount.data
        db.session.commit()
        flash('Item purchases have been updated!', 'success')
        return redirect(url_for('counts.purchases'))
    elif request.method == 'GET':
        form.transdate.data = item.trans_date
        form.itemname.data = item.itemname
        form.casecount.data = item.casecount
    return render_template('update_purchases.html', title='Update Item Purchases', form=form, inv_items=inv_items, item=item, legend='Update Purchases')


@counts.route("/purchases/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_purchases(item_id):
    item = Purchases.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item purchases have been deleted!', 'success')
    return redirect(url_for('counts.purchases'))


@counts.route("/sales/", methods=['GET', 'POST'])
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    sales_items = Sales.query.all()
    group_sales = Sales.query.group_by(Sales.trans_date)
    ordered_sales = group_sales.order_by(
        Sales.trans_date.desc()).paginate(page=page, per_page=10)
    form = EnterSalesForm()
    if form.validate_on_submit():
        sale = Sales(trans_date=form.transdate.data, itemname=form.itemname.data.itemname,
                     eachcount=form.eachcount.data, waste=form.waste.data)
        db.session.add(sale)
        db.session.commit()
        flash(
            f'Sales submitted for {form.itemname.data.itemname} on {form.transdate.data}!', 'success')
        return redirect(url_for('counts.sales'))
    return render_template('sales.html', title='Sales', form=form, sales_items=sales_items, ordered_sales=ordered_sales)


@counts.route("/sales/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_sales(item_id):
    item = Sales.query.get_or_404(item_id)
    inv_items = Sales.query.all()
    form = UpdateSalesForm()
    if form.validate_on_submit():
        item.trans_date = form.transdate.data
        item.itemname = form.itemname.data
        item.eachcount = form.eachcount.data
        item.waste = form.waste.data
        db.session.commit()
        flash('Item Sales have been updated!', 'success')
        return redirect(url_for('counts.sales'))
    elif request.method == 'GET':
        form.transdate.data = item.trans_date
        form.itemname.data = item.itemname
        form.eachcount.data = item.eachcount
        form.waste.data = item.waste
    return render_template('update_sales.html', title='Update Item Sales', form=form, inv_items=inv_items, item=item, legend='Update Sales')


@counts.route("/sales/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_sales(item_id):
    item = Sales.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item Sales have been deleted!', 'success')
    return redirect(url_for('counts.sales'))


@counts.route("/item/new", methods=['GET', 'POST'])
@login_required
def new_item():
    inv_items = Items.query.all()
    form = NewItemForm()
    if form.validate_on_submit():
        item = Items(itemname=form.itemname.data,
                     casepack=form.casepack.data)
        db.session.add(item)
        db.session.commit()
        flash(f'New item created for {form.itemname.data}!', 'success')
        return redirect(url_for('counts.new_item'))
    return render_template('new_item.html', title='New Inventory Item', form=form, inv_items=inv_items, legend='Enter New Item')


@counts.route("/item/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Items.query.get_or_404(item_id)
    inv_items = Items.query.all()
    form = NewItemForm()
    if form.validate_on_submit():
        item.itemname = form.itemname.data
        item.casepack = form.casepack.data
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('counts.new_item'))
    elif request.method == 'GET':
        form.itemname.data = item.itemname
        form.casepack.data = item.casepack
    return render_template('update_item.html', title='Update Inventory Item', form=form, inv_items=inv_items, item=item, legend='Update Item')


@counts.route("/item/<int:item_id>/delete", methods=['POST'])
@login_required
def delete_item(item_id):
    item = Items.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Product has been deleted!', 'success')
    return redirect(url_for('counts.new_item'))
