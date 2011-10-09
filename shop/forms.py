from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from shop.models import Address, Order, Discount, Shopper, Product, Notify

UNITED_KINGDOM = 'united kingdom'
INVALID = 'invalid'
ALBANIA = 'albania'
ANDORRA = 'andorra'
ARMENIA = 'armenia'
AUSTRIA = 'austria'
BELARUS = 'be'
BELGIUM = 'belgium'
BOSNIA_HERZEGOVINA = 'bosnia and herzegovina'
BULGARIA = 'bulgaria'
CAPE_VERDE = 'cape verde'
CROATIA = 'croatia'
CYPRUS = 'cyprus'
CZECH_REPUBLIC = 'czech republic'
DENMARK = 'denmark'
ESTONIA = 'estonia'
FAROE_ISLANDS = 'faroe islands'
FINLAND = 'finland'
FRANCE = 'france'  
GEORGIA = 'georgia'
GERMANY = 'georgia' 
GIBRALTAR = 'gibraltar'
GREECE = 'greece' 
GREENLAND = 'greenland'
HUNGARY = 'hungary'
ICELAND = 'iceland'
IRELAND = 'ireland'  
ITALY = 'italy' 
LATVIA = 'latvia'
LIECHENSTEIN = 'liechenstein'
LITHUANIA = 'lithuania'
LUXEMBOURG = 'luxembourg'  
MACEDONIA = 'macedonia'
MALTA = 'malta'
MOLDOVA = 'moldova'
MONACO = 'monaco' 
NETHERLANDS = 'netherlands'
NORWAY = 'norway'
POLAND = 'poland'
PORTUGAL = 'portugal' 
ROMANIA = 'romania'
SAN_MARINO = 'san marino'
SLOVAK_REPUBLIC = 'slovak republic'
SLOVENIA = 'slovenia'
SPAIN = 'spain'
SWEDEN = 'sweden'
SWITZERLAND = 'switzerland'
TURKEY = 'turkey'
UKRAINE = 'ukraine'
COUNTRY_CHOICES = (
    (UNITED_KINGDOM, u"United Kingdom"),
    (INVALID, u"-----"),
    (ALBANIA, u"Albania"),
    (ANDORRA, u"Andorra"),
    (ARMENIA, u"Armenia"),
    (AUSTRIA, u"Austria"),
    (BELARUS, u"Belarus"),
    (BELGIUM, u"Belgium"),
    (BOSNIA_HERZEGOVINA, u"Bosnia and Herzegovina"),
    (BULGARIA, u"Bulgaria"),
    (CAPE_VERDE, u"Cape Verde"),
    (CROATIA, u"Croatia"),
    (CYPRUS, u"Cyprus"),
    (CZECH_REPUBLIC, u"Czech Republic"),
    (DENMARK, u"Denmark"),
    (ESTONIA, u"Estonia"),
    (FAROE_ISLANDS, u"Faroe Islands"),
    (FINLAND, u"Finland"),
    (FRANCE, u"France"),
    (GEORGIA, u"Georgia"),
    (GERMANY, u"Germany"), 
    (GIBRALTAR, u"Gibraltar"),
    (GREECE, u"Greece"), 
    (GREENLAND, u"Greenland"),
    (HUNGARY, u"Hungary"),
    (ICELAND, u"Iceland"),
    (IRELAND, u"Ireland"),  
    (ITALY, u"Italy"), 
    (LATVIA, u"Latvia"),
    (LIECHENSTEIN, u"Liechenstein"),
    (LITHUANIA, u"Lithuania"),
    (LUXEMBOURG, u"Luxembourg"),  
    (MACEDONIA, u"Macedonia"),
    (MALTA, u"Malta"),
    (MOLDOVA, u"Moldova"),
    (MONACO, u"Monaco"), 
    (NETHERLANDS, u"Netherlands"),
    (NORWAY, u"Norway"),
    (POLAND, u"Poland"),
    (PORTUGAL, u"Portugal"),
    (ROMANIA, u"Romania"),
    (SAN_MARINO, u"San Marino"),
    (SLOVAK_REPUBLIC, u"Slovak Republic"),
    (SLOVENIA, u"Slovenia"),
    (SPAIN, u"Spain"),
    (SWEDEN, u"Sweden"),
    (SWITZERLAND, u"Switzerland"),
    (TURKEY, u"Turkey"),
    (UKRAINE, u"Ukraine"),     
)
 
class AddressAddForm(ModelForm): 
    class Meta:
        model = Address
        exclude = ('owner', 'is_preferred',)
        
            
# handles the submission of their personal details during the order process
class OrderStepOneForm(forms.Form):
    email = forms.EmailField(error_messages={'required': '* Please give an email address', 'invalid': '* Please enter a valid e-mail address.'})
    first_name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your first name'})
    last_name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your surname'})
    house_name_number = forms.CharField(max_length=200, required=False)
    address_line_1 = forms.CharField(max_length=200, required=False)
    address_line_2 = forms.CharField(max_length=200, required=False)
    town_city = forms.CharField(max_length=200, required=False)
    postcode = forms.CharField(max_length=200, required=False)
    subscribed = forms.BooleanField(required=False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        postcode = cleaned_data.get("postcode")
        house_name_number = cleaned_data.get("house_name_number")
        if not postcode:
             if not house_name_number:
                 raise forms.ValidationError("* You must provide a postcode and house name or number")
             else:
                 raise forms.ValidationError("* You must provide a postcode")
        
        if not house_name_number:
                raise forms.ValidationError("* You must provide a house name or number")
        
        
        return cleaned_data

class UpdateDiscountForm(forms.Form):
    discount_code = forms.CharField(required=True)

# handles the contact us form
class ContactForm(forms.Form):
    your_name = forms.CharField(required=True)
    your_email = forms.EmailField(required=True, error_messages={'required': 'Please enter a valid email address'})
    your_message = forms.CharField(widget=forms.Textarea, required=False)

class UpdateProfileForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False, error_messages={'required': 'Please enter a valid email address'})
  
# the form for submitting a tell-a-friend email address
class TellAFriendForm(forms.Form):
    recipient = forms.EmailField(required=True, error_messages={'required': '* You must give an email address for your friend'})
    sender = forms.EmailField(required=True, error_messages={'required': '* You must give your own email address'})
    message = forms.CharField(required=False, widget=forms.Textarea)

# after the user has finished ordering, handles submission of their twitter username
class SubmitTwitterForm(forms.Form):
    twitter_username = forms.CharField()
    
# handles the testimonials or reviews of a particular tea (views.review)
class ReviewForm(forms.Form):
    text = forms.CharField(required=True, widget=forms.Textarea)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True, error_messages={'required': '* You must give a valid email address'})

class NotifyForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': 'Please enter a valid email address'})