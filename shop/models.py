from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime, timedelta

from slugify import smart_slugify
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from christmas import settings





# these are the categories of products on the site.
PRODUCT_CATEGORY = (
    (u'TEA', u'Tea'),
    (u'PACK', u'Package'),
    (u'OTH', u'Other'),
    (u'POS', u'Postage'),
)

# these are the country choices for an address
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
RUSSIA = 'russia'
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
    (RUSSIA, u"Russia"),
    (SAN_MARINO, u"San Marino"),
    (SLOVAK_REPUBLIC, u"Slovak Republic"),
    (SLOVENIA, u"Slovenia"),
    (SPAIN, u"Spain"),
    (SWEDEN, u"Sweden"),
    (SWITZERLAND, u"Switzerland"),
    (TURKEY, u"Turkey"),
    (UKRAINE, u"Ukraine"),     
)



class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
    meta_title = models.CharField(max_length=200, blank=True, null=True)		
    description = models.TextField()
    meta_description = models.TextField(blank=True, null=True)
    super_short_description = models.CharField(max_length=200)
    body_text = models.TextField()
    long_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/product-photos')
    image_2 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_2_caption = models.CharField(max_length=200, blank=True)
    image_3 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_3_caption = models.CharField(max_length=200, blank=True)
    image_4 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_4_caption = models.CharField(max_length=200, blank=True)
    image_5 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_5_caption = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=3, choices=PRODUCT_CATEGORY)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    coming_soon = models.BooleanField(default=False)
        
    def __unicode__(self):
        return self.name
      
    def get_absolute_url(self):
        return "/teas/%s/" % self.slug  #important, do not change
    
    def get_lowest_price(self):
        try:
            prices = UniqueProduct.objects.filter(parent_product=self, is_sale_price=False).order_by('price')[0]
        except:
            prices = None
        return prices
    
    def get_reviews(self):
        reviews = Review.objects.filter(product=self)
        return reviews    
    
    def save(self, force_insert=False, force_update=False):
         super(Product, self).save(force_insert, force_update)
         try:
             ping_google()
         except Exception:
             # Bare 'except' because we could get a variety
             # of HTTP-related exceptions.
             pass 
 
class UniqueProduct(models.Model):
    weight = models.IntegerField(null=True, blank=True)
    weight_unit = models.CharField(help_text="Weight units", max_length=3, null=True, blank=True)
    price = models.DecimalField(help_text="Price", max_digits=8, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(help_text="Currency", max_length=3, null=True, blank=True)
    parent_product = models.ForeignKey(Product)
    description = models.TextField()
    available_stock = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # bool
    is_sale_price = models.BooleanField(default=False)
    # numeric(8, 2)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="If it's a sale item, what was the old price?")
    
    def __unicode__(self):
        return "%s (%s%s)" % (self.parent_product, self.weight, self.weight_unit)
                

class Shopper(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    number_referred = models.IntegerField(null=True, blank=True)
    subscribed = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200)
    twitter_username = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.email
        
    def get_addresses(self):
        addresses = Address.objects.filter(owner=self).order_by('-id')
        return addresses 
    
    def get_orders(self):
        orders = Order.objects.filter(owner=self).order_by('-date_paid')
        return orders
    
    def get_value(self):
        value = 0
        for order in self.get_orders():
            amount = order.get_amount()
            value += amount
        
        return value
            
class Review(models.Model):
    product = models.ForeignKey(Product)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    text = models.TextField()
    short_text = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.product.name       
            
class Address(models.Model):
    owner = models.ForeignKey(Shopper)
    house_name_number = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    town_city = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, db_index=True)
    
    def __unicode__(self):
        return "%s, %s, %s" % (self.house_name_number, self.postcode, self.country)
    
       
        
class Basket(models.Model):
    date_modified = models.DateTimeField()
    owner = models.ForeignKey(Shopper, null=True) #can delete this
    
    def __unicode__(self):
        return str(self.date_modified)
 

class BasketItem(models.Model):  
    item = models.ForeignKey(UniqueProduct)
    quantity = models.PositiveIntegerField()
    basket = models.ForeignKey(Basket)
    
    def get_price(self):
        price = self.quantity * self.item.price
        return price
        
    def __unicode__(self):
        return "%s x %s" % (self.item, self.quantity)

    
class Discount(models.Model):
    discount_code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    discount_value = models.DecimalField(max_digits=3, decimal_places=2)
    
    
class Order(models.Model):
    items = models.ManyToManyField(BasketItem)
    is_confirmed_by_user = models.BooleanField(default=False)
    date_confirmed = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    is_giveaway = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True)
    address = models.ForeignKey(Address, null=True)
    owner = models.ForeignKey(Shopper)
    discount = models.ForeignKey(Discount, null=True, blank=True)
    invoice_id = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)
    sampler_email_sent = models.BooleanField(default=False)
    sampler_sent = models.BooleanField(default=False)
    
    STATUS_CREATED_NOT_PAID = 'created not paid'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_ADDRESS_PROBLEM = 'address problem'
    STATUS_PAYMENT_FLAGGED = 'payment flagged'
    STATUS_CHOICES = (
            (STATUS_CREATED_NOT_PAID, u"Created, not paid"),
            (STATUS_PAID, u"Paid"),
            (STATUS_SHIPPED, u"Shipped"),
            (STATUS_ADDRESS_PROBLEM, u"Address problem"),
            (STATUS_PAYMENT_FLAGGED, u"Payment flagged"),     
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    review_email_sent = models.BooleanField(default=False)
    
    
    def get_discount(self):
        total_price = 0
        for item in self.items:
            price = item.quantity * item.item.price
            total_price += price
        discount_amount = total_price * self.discount.discount_value
        return discount_amount
    
    def __unicode__(self):
        return self.invoice_id
    
    def get_amount(self):
        amount = 0
        for item in self.items.all():
            amount += item.get_price()
        if amount > 50:
            pass
        else:
            amount += 3
        return amount
    

    def ready_to_send_review(self):
        if (self.date_paid + timedelta(days=7)) < datetime.now():
            review = True
        else:
            review = False
        return review
    
    def ready_to_send_sampler_email(self):
        if (self.date_paid + timedelta(days=14)) < datetime.now():
            sampler = True
        else:
            sampler = False
        return sampler

    
# can be deleted, not used anymore (Aug 2011)
class WeLike(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    url = models.URLField()
    image = models.ImageField(upload_to='images/likes')
    date_added = models.DateTimeField(default=datetime.now)
    
    def __unicode__(self):
        return self.title
    
    # still need to do this properly
    def get_short_url(self):
        return url
          
     

class Photo(models.Model):
    shopper = models.ForeignKey(Shopper)
    photo = models.ImageField(upload_to='images/user-submitted')
    published = models.BooleanField(default=False)
    published_homepage = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    related_product = models.ForeignKey(Product, blank=True, null=True)
    
    def __unicode__(self):
        return self.shopper.email
    
    def get_absolute_url(self):
        return "/tea-lover/%s/" % self.shopper.slug


class Referee(models.Model):
    email = models.EmailField()
    date = models.DateTimeField('date_referred', default=datetime.now)
    referred_by = models.ForeignKey(Shopper)
    
    def __unicode__(self):
        return self.email
       

class Notify(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=200, blank=True, null=True)
    product = models.ForeignKey(Product, blank=True, null=True)
    date = models.DateTimeField('date', default=datetime.now,
        help_text="The date that they made contact")
    email_sent = models.BooleanField(default=False, help_text="If this is ticked, don't send them emails again")

    def __unicode__(self):
        return self.email

class Page(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    content = models.TextField()
    template = models.CharField(max_length=200, blank=True, null=True)
    right_side_boxes = models.CharField(max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        if self.parent:
            if self.parent.parent:
                if self.parent.parent.parent:
                    url = "/%s/%s/%s/%s/" % (self.parent.parent.parent.slug, self.parent.parent.slug, self.parent.slug, self.slug)
                else:
                    url = "/%s/%s/%s/" % (self.parent.parent.slug, self.parent.slug, self.slug)
            else:
                url = "/%s/%s/" % (self.parent.slug, self.slug)
        else:
            url = "/%s/" % (self.slug)
            
        return url
    
    def get_children(self):
        pages = Page.objects.filter(parent=self)
        return pages


# signals to connect to receipt of PayPal IPNs

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    if order.status == Order.STATUS_PAID:
        return
        
    order.status = Order.STATUS_PAID
    order.date_paid = ipn_obj.payment_date
    order.is_paid = True
    order.save()
    
    # create and send an email to the customer
    to_email = order.owner.email
    from_email = settings.SITE_EMAIL
    subject = "Order confirmed - Min River Tea Farm" 
    
    text_content = render_to_string('shop/emails/text/order_confirm_customer.txt', {
    	        'first_name': order.owner.first_name, 
    	        'invoice_id': order.invoice_id, 
    	        'order_items': order.items.all(), 
    })
    
    html_content = render_to_string('shop/emails/html/html_order_confirm_customer.html', {
                'first_name': order.owner.first_name,
                'invoice_id':	order.invoice_id,
                'order_item': order.items.all(),
                'subject': subject,
    })
    
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
     
    # create and send an email to me
    invoice_id = order.invoice_id
    body = render_to_string('shop/emails/text/order_confirm_admin.txt', {
    	        'email': to_email, 
    	        'invoice_id': invoice_id, 
    	        'order_items': order.items.all(), 
    	        'order_status': order.status})
    subject_line = "NEW ORDER - %s" % invoice_id      
      
    send_mail(
                  subject_line, 
                  body, 
                  from_email,
                  [from_email], 
                  fail_silently=False
     )  
payment_was_successful.connect(show_me_the_money)    

    
def payment_flagged(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    order.status = Order.STATUS_PAYMENT_FLAGGED
    order.save()

     # create and send an email to me
    invoice_id = order.invoice_id
    email = order.owner.email
    recipient = 'mail@christmastea.com'
    body = render_to_string('shop/emails/text/order_confirm_admin.txt', {'email': email, 'invoice_id': invoice_id, 'order_items': order.items.all()})
    subject_line = "FLAGGED ORDER - %s" % invoice_id 
    email_sender = 'mail@christmastea.com'
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )   
payment_was_flagged.connect(payment_flagged)






