from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, SelectMultipleField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange, InputRequired
from wtforms.widgets import ListWidget, CheckboxInput


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address (e.g., name@example.com)')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')
    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address (e.g., name@example.com)')
    ])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    submit = SubmitField('Login')


class PreferenceForm(FlaskForm):
    # Basic Info
    preference_name = StringField('Profile Name', validators=[Optional()])
    save_preference = BooleanField('Save these preferences')
    
    # Cooking Constraints
    max_time = IntegerField('Maximum Cooking Time (minutes)', 
                           validators=[Optional(), NumberRange(min=0, max=240)])
    difficulty = SelectField('Difficulty Level', 
                           choices=[('', 'Any'), ('easy', 'Easy'), 
                                    ('medium', 'Medium'), ('hard', 'Hard')],
                           validators=[Optional()])
    
    # Dietary Needs
    diet = SelectField('Dietary Preference', 
                      choices=[
                          ('', 'No Restrictions'),
                          ('vegetarian', 'Vegetarian'),
                          ('vegan', 'Vegan'),
                          ('gluten-free', 'Gluten Free')
                      ], 
                      validators=[Optional()])
    
    allergies = MultiCheckboxField('Allergies',
                                 choices=[
                                     ('dairy', 'Dairy Free'),
                                     ('gluten', 'Gluten Free'),
                                     ('nuts', 'Nut Free')
                                 ])
    
    max_calories = IntegerField('Maximum Calories', 
                          validators=[Optional(), NumberRange(min=0, max=5000)])
    
    submit = SubmitField('Find Recipes')