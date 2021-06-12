from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from dailycount.models import Items


def item_query():
    return Items.query


class NewItemForm(FlaskForm):
    itemname = StringField('Item Name', validators=[DataRequired()])
    casepack = IntegerField('Case Pack', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EnterCountForm(FlaskForm):
    transdate = DateField('Count Date', format='%Y-%m-%d')
    am_pm = SelectField('Count Type', choices=['Opening', 'Closing'])
    itemname = QuerySelectField('Item Name',
                                query_factory=item_query, allow_blank=True, get_label='itemname')
    casecount = IntegerField('Case Count')
    eachcount = IntegerField('Each Count')
    submit = SubmitField('Submit!')


class UpdateCountForm(FlaskForm):
    transdate = DateField('Count Date', format='%Y-%m-%d')
    am_pm = SelectField('Count Type', choices=['Opening', 'Closing'])
    itemname = StringField('Item Name', validators=[DataRequired()])
    casecount = IntegerField('Case Count')
    eachcount = IntegerField('Each Count')
    submit = SubmitField('Submit!')


class EnterPurchasesForm(FlaskForm):
    transdate = DateField('Purchase Date', format='%Y-%m-%d')
    itemname = QuerySelectField('Item Name',
                                query_factory=item_query, allow_blank=True, get_label='itemname')
    casecount = IntegerField('Cases Purchased')
    submit = SubmitField('Submit!')


class UpdatePurchasesForm(FlaskForm):
    transdate = DateField('Purchase Date', format='%Y-%m-%d')
    itemname = StringField('Item Name', validators=[DataRequired()])
    casecount = IntegerField('Cases Purchased')
    submit = SubmitField('Submit!')


class EnterSalesForm(FlaskForm):
    transdate = DateField('Sales Date', format='%Y-%m-%d')
    itemname = QuerySelectField('Item Name',
                                query_factory=item_query, allow_blank=True, get_label='itemname')
    eachcount = IntegerField('Each Sales')
    waste = IntegerField('Waste')
    submit = SubmitField('Submit!')


class UpdateSalesForm(FlaskForm):
    transdate = DateField('Sales Date', format='%Y-%m-%d')
    itemname = StringField('Item Name', validators=[DataRequired()])
    eachcount = IntegerField('Each Sales')
    waste = IntegerField('Waste')
    submit = SubmitField('Submit!')