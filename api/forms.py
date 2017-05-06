import wtforms_json
from flask_wtf import Form, FlaskForm
from wtforms import StringField, BooleanField, FormField, FieldList
from wtforms import validators

wtforms_json.init()


class EdgeForm(Form):
    from_node = StringField('from', [validators.required()])
    to_node = StringField('to', [validators.required()])


class ParseForm(FlaskForm):
    start = StringField('start', [validators.required()])
    end = StringField('end', [validators.required()])
    edges = FieldList(FormField(EdgeForm), 'edges', [validators.required()])
    verbose = BooleanField('verbose', default=False)
