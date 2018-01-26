import tw2.core as twc
import tw2.forms as twf
from formencode.compound import All
from formencode import validators 

name_validator=All(
    validators.NotEmpty(),
    validators.UnicodeString(),
    validators.Regex(r'[A-Za-z]')
)

phone_validator=All(
    validators.NotEmpty(),
    validators.UnicodeString(),
    validators.Regex(r'[0-9]')
)
class SubmitForm(twf.Form):
    class child(twf.TableLayout):
        nome = twf.TextField(size=15, validator=name_validator)
        telefono = twf.TextField(size=15, validator=phone_validator)
        submit = twf.SubmitButton(value='Submit')
    action = '/save'
