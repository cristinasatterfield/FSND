from datetime import datetime
from flask_wtf import Form, CsrfProtect
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import (
    InputRequired,
    AnyOf,
    URL,
    ValidationError,
    Optional,
    Length,
    Regexp,
)


class RequiredIf(InputRequired):
    # makes a field required if another field is set
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field.data == "True":
            super(RequiredIf, self).__call__(form, field)


class FutureDate(object):
    # validates that a date is in the future
    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = "Date invalid. Date cannot be in the past."
        self.message = message

    def __call__(self, form, field):
        print("Field data - Future Date", field.data)
        if field.data < datetime.today():
            raise ValidationError(self.message)


class ShowForm(Form):
    artist = SelectField(
        "artist",
        coerce=int,
        validators=[InputRequired(message="Please select an artist.")],
    )
    venue = SelectField(
        "venue",
        coerce=int,
        validators=[InputRequired(message="Please select a venue.")],
    )
    start_time = DateTimeField(
        "start_time",
        validators=[
            InputRequired(
                message="Input is invalid or missing. Use format: YYYY-MM-DD HH:MM:SS"
            ),
            FutureDate(),
        ],
        default=datetime.today(),
    )


class VenueForm(Form):
    name = StringField(
        "name",
        validators=[
            InputRequired(message="Please input a venue name."),
            Length(
                max=120, message="Venue name must be less than 120 characters long."
            ),
        ],
    )
    image_link = StringField(
        "image_link",
        validators=[
            Optional(),
            URL(message="Image link is invalid. Use format: http://..."),
        ],
    )
    city = StringField(
        "city",
        validators=[
            InputRequired(message="Please input a city."),
            Length(max=120, message="City name must be less than 120 characters long."),
        ],
    )
    state = SelectField(
        "state",
        validators=[InputRequired(message="Please select a state.")],
        choices=[
            ("AL", "AL"),
            ("AK", "AK"),
            ("AZ", "AZ"),
            ("AR", "AR"),
            ("CA", "CA"),
            ("CO", "CO"),
            ("CT", "CT"),
            ("DE", "DE"),
            ("DC", "DC"),
            ("FL", "FL"),
            ("GA", "GA"),
            ("HI", "HI"),
            ("ID", "ID"),
            ("IL", "IL"),
            ("IN", "IN"),
            ("IA", "IA"),
            ("KS", "KS"),
            ("KY", "KY"),
            ("LA", "LA"),
            ("ME", "ME"),
            ("MT", "MT"),
            ("NE", "NE"),
            ("NV", "NV"),
            ("NH", "NH"),
            ("NJ", "NJ"),
            ("NM", "NM"),
            ("NY", "NY"),
            ("NC", "NC"),
            ("ND", "ND"),
            ("OH", "OH"),
            ("OK", "OK"),
            ("OR", "OR"),
            ("MD", "MD"),
            ("MA", "MA"),
            ("MI", "MI"),
            ("MN", "MN"),
            ("MS", "MS"),
            ("MO", "MO"),
            ("PA", "PA"),
            ("RI", "RI"),
            ("SC", "SC"),
            ("SD", "SD"),
            ("TN", "TN"),
            ("TX", "TX"),
            ("UT", "UT"),
            ("VT", "VT"),
            ("VA", "VA"),
            ("WA", "WA"),
            ("WV", "WV"),
            ("WI", "WI"),
            ("WY", "WY"),
        ],
    )
    address = StringField(
        "address",
        validators=[
            InputRequired(message="Please input an address."),
            Regexp(
                r"\s*\d{1,6}\s([a-zA-Z0-9]{1,25}\s?)+$", message="Address is invalid.",
            ),
        ],
    )
    phone = StringField(
        "phone",
        validators=[
            InputRequired(message="Please input a phone number."),
            Regexp(
                r"^(\d{3}-){2}\d{4}$",
                message="Phone number is invalid. Use the format: ###-###-####",
            ),
        ],
    )
    genres = SelectMultipleField(
        "genres",
        coerce=int,
        validators=[InputRequired(message="Please select at least one genre.")],
    )
    website_link = StringField(
        "website_link",
        validators=[
            Optional(),
            URL(message="Website link is invalid. Use format: http://..."),
        ],
    )
    facebook_link = StringField(
        "facebook_link",
        validators=[
            Optional(),
            URL(message="Facebook link is invalid. Use format: http://..."),
        ],
    )
    seeking_talent = SelectField(
        "seeking_talent",
        validators=[
            InputRequired(message="Are you currently seeking talent? Select yes or no.")
        ],
        choices=[("False", "No"), ("True", "Yes")],
    )
    seeking_description = StringField(
        "seeking_description",
        validators=[
            RequiredIf("seeking_talent"),
            Length(
                max=500, message="Description must be less than 500 characters long."
            ),
        ],
    )


class ArtistForm(Form):
    name = StringField(
        "name",
        validators=[
            InputRequired(message="Please input an artist name."),
            Length(
                max=120, message=" Artist name must be less than 120 characters long."
            ),
        ],
    )
    image_link = StringField(
        "image_link",
        validators=[
            Optional(),
            URL(message="Image link is invalid. Use format: http://..."),
        ],
    )
    city = StringField(
        "city",
        validators=[
            InputRequired(message="Please input a city."),
            Length(
                max=120, message=" City name must be less than 120 characters long."
            ),
        ],
    )
    state = SelectField(
        "state",
        validators=[InputRequired(message="Please select a state.")],
        choices=[
            ("AL", "AL"),
            ("AK", "AK"),
            ("AZ", "AZ"),
            ("AR", "AR"),
            ("CA", "CA"),
            ("CO", "CO"),
            ("CT", "CT"),
            ("DE", "DE"),
            ("DC", "DC"),
            ("FL", "FL"),
            ("GA", "GA"),
            ("HI", "HI"),
            ("ID", "ID"),
            ("IL", "IL"),
            ("IN", "IN"),
            ("IA", "IA"),
            ("KS", "KS"),
            ("KY", "KY"),
            ("LA", "LA"),
            ("ME", "ME"),
            ("MT", "MT"),
            ("NE", "NE"),
            ("NV", "NV"),
            ("NH", "NH"),
            ("NJ", "NJ"),
            ("NM", "NM"),
            ("NY", "NY"),
            ("NC", "NC"),
            ("ND", "ND"),
            ("OH", "OH"),
            ("OK", "OK"),
            ("OR", "OR"),
            ("MD", "MD"),
            ("MA", "MA"),
            ("MI", "MI"),
            ("MN", "MN"),
            ("MS", "MS"),
            ("MO", "MO"),
            ("PA", "PA"),
            ("RI", "RI"),
            ("SC", "SC"),
            ("SD", "SD"),
            ("TN", "TN"),
            ("TX", "TX"),
            ("UT", "UT"),
            ("VT", "VT"),
            ("VA", "VA"),
            ("WA", "WA"),
            ("WV", "WV"),
            ("WI", "WI"),
            ("WY", "WY"),
        ],
    )
    phone = StringField(
        "phone",
        validators=[
            InputRequired("Please input a phone number."),
            Regexp(
                r"^(\d{3}-){2}\d{4}$",
                message="Phone number is invalid. Use the format: ###-###-####",
            ),
        ],
    )
    genres = SelectMultipleField(
        "genres",
        coerce=int,
        validators=[InputRequired(message="Please select at least one genere.")],
    )
    website_link = StringField(
        "website_link",
        validators=[
            Optional(),
            URL(message="Website link is invalid. Use format: http://..."),
        ],
    )
    facebook_link = StringField(
        "facebook_link",
        validators=[
            Optional(),
            URL(message="Facebook link is invalid. Use format: http://..."),
        ],
    )
    seeking_venue = SelectField(
        "seeking_venue",
        validators=[
            InputRequired(
                message="Are you currently seeking a venue? Select yes or no."
            )
        ],
        choices=[("False", "No"), ("True", "Yes")],
    )
    seeking_description = StringField(
        "seeking_description",
        validators=[
            RequiredIf("seeking_venue"),
            Length(
                max=500, message="Description must be less than 500 charaters long."
            ),
        ],
    )
