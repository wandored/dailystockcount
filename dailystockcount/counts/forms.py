from datetime import datetime
from flask_wtf import FlaskForm, Form
from wtforms import StringField, SubmitField, SelectField, IntegerField, HiddenField, FieldList, FormField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from dailystockcount.models import Items


def item_query():
    return Items.query


def item_number():
    return Items.query.count()


class NewItemForm(FlaskForm):
    itemname = StringField('Item Name: ',
                           validators=[DataRequired()])
    casepack = IntegerField('# per Case: ',
                            validators=[DataRequired()])
    submit = SubmitField('Submit')


class UpdateItemForm(FlaskForm):
    itemname = StringField('Item Name: ',
                           validators=[DataRequired()])
    casepack = IntegerField('# per Case: ',
                            validators=[DataRequired()])
    submit = SubmitField('Submit')


class EnterCountForm(FlaskForm):
    transdate = DateField('Count Date: ',
                          format='%Y-%m-%d',
                          default=datetime.today)
    am_pm = SelectField('Count Type: ',
                        choices=['PM', 'AM'])
    itemname = QuerySelectField('Item Name: ',
                                query_factory=item_query,
                                allow_blank=True,
                                get_label='itemname')
    casecount = IntegerField('Case Count: ',
                             default=0)
    eachcount = IntegerField('Each Count: ',
                             default=0)
    submit = SubmitField('Submit!')


class UpdateCountForm(FlaskForm):
    transdate = DateField('Count Date: ',
                          format='%Y-%m-%d')
    am_pm = SelectField('Count Type: ',
                        choices=['PM', 'AM'])
    itemname = StringField('Item Name: ',
                           validators=[DataRequired()])
    casecount = IntegerField('Case Count: ')
    eachcount = IntegerField('Each Count: ')
    submit = SubmitField('Submit!')


class PurchaseForm(Form):
    itemname = QuerySelectField('Item Name: ',
                                query_factory=item_query,
                                allow_blank=True,
                                get_label='itemname')
    casecount = IntegerField('Cases Purchased: ',
                             default=0)


class EnterPurchasesForm(FlaskForm):
    transdate = DateField('Purchase Date: ',
                          format='%Y-%m-%d',
                          default=datetime.today)
    am_pm = HiddenField('PM')
#    itemname = FieldList(FormField(PurchaseForm), min_entries=5)
    itemname = QuerySelectField('Item Name: ',
                                query_factory=item_query,
                                allow_blank=True,
                                get_label='itemname')
    casecount = IntegerField('Cases Purchased: ', default=0)
    submit = SubmitField('Submit!')


class UpdatePurchasesForm(FlaskForm):
    transdate = DateField('Purchase Date: ',
                          format='%Y-%m-%d')
    am_pm = HiddenField('PM')
    itemname = StringField('Item Name',
                           validators=[DataRequired()])
    casecount = IntegerField('Cases Purchased')
    submit = SubmitField('Submit!')


class EnterSalesForm(FlaskForm):
    transdate = DateField('Sales Date: ',
                          format='%Y-%m-%d',
                          default=datetime.today)
    am_pm = HiddenField('PM')
    itemname = QuerySelectField('Item Name: ',
                                query_factory=item_query,
                                allow_blank=True,
                                get_label='itemname')
    eachcount = IntegerField('Each Sales: ',
                             default=0)
    waste = IntegerField('Waste',
                         default=0)
    submit = SubmitField('Submit!')


class UpdateSalesForm(FlaskForm):
    transdate = DateField('Sales Date: ',
                          format='%Y-%m-%d')
    am_pm = HiddenField('PM')
    itemname = StringField('Item Name: ',
                           validators=[DataRequired()])
    eachcount = IntegerField('Each Sales: ')
    waste = IntegerField('Waste: ')
    submit = SubmitField('Submit!')
