from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class WorkoutForm(FlaskForm):
    exercise_name = StringField('Exercise Name', validators=[
        DataRequired(message='Exercise name is required.'),
        Length(min=2, max=100, message='Name must be 2–100 characters.')
    ])
    category = SelectField('Category', choices=[
        ('strength', 'Strength'),
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
        ('sports', 'Sports'),
        ('other', 'Other')
    ])
    duration = IntegerField('Duration (min)', validators=[
        DataRequired(message='Duration is required.'),
        NumberRange(min=1, max=600, message='Must be 1–600 minutes.')
    ])
    sets = IntegerField('Sets', validators=[Optional(), NumberRange(min=1, max=100)])
    reps = IntegerField('Reps', validators=[Optional(), NumberRange(min=1, max=1000)])
    weight = FloatField('Weight (lbs)', validators=[Optional(), NumberRange(min=0, max=2000)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
