from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm
from django.http import HttpResponseRedirect 
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse


import urllib
import urllib2
import xml.etree.ElementTree as etree
from django.utils import simplejson

from PIL import Image
from cStringIO import StringIO
import os, md5
import datetime
import uuid
import re

from christmas.shop.models import *
from christmas.shop.forms import *
from christmas.slugify import smart_slugify



class BasketItemDoesNotExist(Exception):
    pass
    
class BasketDoesNotExist(Exception):
    pass
    

#render shortcut
def render(request, template, context_dict=None, **kwargs):
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )

def GetCountry(request):
    # this is coming from http://ipinfodb.com JSON api
    # the variables
    apikey = settings.IPINFO_APIKEY 
    ip = request.META.get('REMOTE_ADDR')
    baseurl = "http://api.ipinfodb.com/v3/ip-country/?key=%s&ip=%s&format=json" % (apikey, ip)
    urlobj = urllib2.urlopen(baseurl)
    
    # get the data
    url = baseurl + "?" + apikey + "?"
    data = urlobj.read()
    urlobj.close()
    datadict = simplejson.loads(data)
    return datadict
    

# the homepage view
def index(request):
    review = Review.objects.all().order_by('?')[:2]
    products = UniqueProduct.objects.all()
    return render(request, "shop/home.html", locals())

def page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    nav_items = Page.objects.filter(parent=page)
    if page.template:
        template = page.template
    else:
        template = "shop/page.html"
    return render(request, template, locals())


def sub_page(request, slug, sub_slug):
    page = get_object_or_404(Page, slug=sub_slug)
    nav_items = Page.objects.filter(parent=page.parent)
    if page.template:
        template = page.template
    else:
        template = "shop/page.html"
    return render(request, "shop/page.html", locals())
 
def sub_sub_page(request, slug, sub_slug, sub_sub_slug):
    page = get_object_or_404(Page, slug=sub_sub_slug)
    nav_items = Page.objects.filter(parent=page.parent.parent)
    if page.template:
        template = page.template
    else:
        template = "shop/page.html"
    return render(request, "shop/page.html", locals())

def sub_sub_sub_page(request, slug, sub_slug, sub_sub_slug, sub_sub_sub_slug):
    page = get_object_or_404(Page, slug=sub_sub_sub_slug)
    nav_items = Page.objects.filter(parent=page.parent.parent.parent)
    if page.template:
        template = page.template
    else:
        template = "shop/page.html"
    return render(request, "shop/page.html", locals())
   
# the product listing page
def products(request):
    try:
        added = request.session['ADDED']
    except:
        added = None
       
    if added:
        thing = get_object_or_404(BasketItem, id=request.session['ADDED'])
        message = "1 x %s%s added to your basket!" % (thing.item.weight, thing.item.weight_unit)
        request.session['ADDED'] = None
        
    products = Product.objects.filter(is_active=True)
    prices = UniqueProduct.objects.filter(is_active=True, is_sale_price=False)
    products_and_prices = []
    for product in products:
        products_and_prices.append((product, prices.filter(parent_product=product)))

    return render(request, "shop/teas.html", locals())

def sale(request):
    prices = UniqueProduct.objects.filter(is_active=True, is_sale_price=True)
    return render(request, "shop/sale.html", locals())

# view for a single product
def product_view(request, slug):
    try:
        added = request.session['ADDED']
    except:
        added = None
    
    try:
        notify_message = request.session['NOTIFY']
        request.session['NOTIFY'] = None
    except:
        notify_message = None
       
    if added:
        thing = get_object_or_404(BasketItem, id=request.session['ADDED'])
        message = "1 x %s%s added to your basket!" % (thing.item.weight, thing.item.weight_unit)
        request.session['ADDED'] = None
    
    tea = get_object_or_404(Product, slug=slug)
    prices = UniqueProduct.objects.filter(parent_product=tea, is_active=True, is_sale_price=False).order_by('price')
    others = Product.objects.filter(is_active=True).exclude(id=tea.id)
    reviews = Review.objects.filter(product=tea.id, is_published=True)[:2]
    
    # here we're handling the notify form, if the product is out of stock
    if request.method == 'POST':
        form = NotifyForm(request.POST)
        if form.is_valid():
            Notify.objects.create(
                name="",
                email=form.cleaned_data['email'],
                product=tea,
            )
            
            request.session['NOTIFY'] = "1"
            url = request.META.get('HTTP_REFERER','/')
            return HttpResponseRedirect(url)
    
    else:
        form = NotifyForm()

    return render(request, "shop/tea_view.html", locals())
    
def contact_us(request):
    try:
        if request.session['MESSAGE'] == "1":
            message = True
            request.session['MESSAGE'] = ""
    except:
        pass 
        
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            
            # get cleaned data from form submission
            message = form.cleaned_data['your_message']
            your_name = form.cleaned_data['your_name']
            your_email = form.cleaned_data['your_email']
            
            # create email
            body = render_to_string('shop/emails/text/contact_template.txt', {
            	 'message': message,
            	 'your_email': your_email,
            	 'your_name': your_name,
            })

            recipient = settings.SITE_EMAIL
            sender = settings.SITE_EMAIL
            subject_line = "christmasTEA.COM - WEBSITE CONTACT SUBMISSION"
                
            send_mail(
                          subject_line, 
                          body, 
                          sender,
                          [recipient], 
                          fail_silently=False
            )
            
            
            url = request.META.get('HTTP_REFERER','/')
            request.session['MESSAGE'] = "1"
            return HttpResponseRedirect(url) 
    else:
        form = ContactForm() 
    
    return render(request, "shop/forms/contact_form.html", locals())        
   
# function for adding stuff to your basket
def add_to_basket(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    if request.user.is_anonymous:
        try:
            #try to find out if they already have a session open
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except:
            #if not, we'll create one.
            basket = Basket.objects.create(date_modified=datetime.now())
            basket.save()
            request.session['BASKET_ID'] = basket.id
     
    try:
        item = BasketItem.objects.get(
            basket=basket,
            item=product,
        )
    except:
        item = BasketItem.objects.create(item=product, quantity=1, basket=basket)
        item.save()
        
    else:
        item.quantity += 1
        item.save()
        
    url = request.META.get('HTTP_REFERER','/')
    request.session['ADDED'] = item.id
    return HttpResponseRedirect(url)


# function for removing stuff from your basket
def remove_from_basket(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    if request.user.is_anonymous:
        #try to find out if they alread have a session cookie open with a basket
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        # if not, we'll return an error because nobody can remove an item 
        # from a basket that doesn't exist
        except BasketDoesNotExist:
            pass
    
    item = BasketItem.objects.get(
        basket=basket,
        item=product,
    )
    item.delete()
    
    return HttpResponseRedirect('/basket/') # Redirect after POST
    
# function for reducing the quantity of an item in your basket    
def reduce_quantity(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    # GET THE USER'S BASKET
    if request.user.is_anonymous:
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except BasketDoesNotExist:
            pass
    
    basket_item = BasketItem.objects.get(basket=basket, item=product)
    if basket_item.quantity > 1:
        basket_item.quantity -= 1
        basket_item.save()
    else:
        pass
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# function for increasing the quantity of an item in your basket
def increase_quantity(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    # GET THE USER'S BASKET
    if request.user.is_anonymous:
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except BasketDoesNotExist:
            pass

    
    basket_item = BasketItem.objects.get(basket=basket, item=product)
    basket_item.quantity += 1
    basket_item.save()
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# the view for your basket
def basket(request):

    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    except:
        basket = None        
                
    basket_items = BasketItem.objects.filter(basket=basket)
    total_price = 0
    for item in basket_items:
        price = item.quantity * item.item.price
        total_price += price
    
    if total_price > 50:
        postage_discount = True
    else:
        total_price += 3
        
    discount_form = UpdateDiscountForm()
        
    return render(request, "shop/basket.html", locals())



# the view for order process step 1 - adding your details
def order_step_one(request):
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
    except:
        problem = "You don't have any items in your basket, so you can't process an order!"
        return render(request, 'shop/order-problem.html', locals())   

    try:
        order = get_object_or_404(Order, invoice_id=request.session['ORDER_ID'])
        # load their data from cookie
        if not order == None:    
            email = order.owner.email
            house_name_number = order.address.house_name_number
            address_line_1 = order.address.address_line_1
            address_line_2 = order.address.address_line_2
            town_city = order.address.town_city
            postcode = order.address.postcode
            first_name = order.owner.first_name
            last_name = order.owner.last_name
    except:
        pass
    
    if request.user.is_authenticated():
        shopper = get_object_or_404(Shopper, user=request.user.id)

    if request.method == 'POST': 
        form = OrderStepOneForm(request.POST)
        
        # if the form has no errors...
        if form.is_valid(): 
        
            # get or create a user object
            if request.user.is_authenticated():
                this_user = request.user
            else:
                try:
                    this_user = get_object_or_404(User, email=form.cleaned_data['email'])
                except:
                    username = form.cleaned_data['email']
                    random_password = uuid.uuid1().hex
                    creation_args = {
                        'username': form.cleaned_data['email'],
                        'email': form.cleaned_data['email'],
                        'password': random_password,
                    }
                     
                    this_user = User.objects.create(**creation_args)
                    this_user.first_name = form.cleaned_data['first_name']
                    this_user.last_name = form.cleaned_data['last_name']
                    this_user.save()
                
                        
            # create a 'shopper' object
            try:
                shopper = get_object_or_404(Shopper, user=this_user.id)
            except:
                full_name = "%s %s" % (form.cleaned_data['first_name'], form.cleaned_data['last_name'])
                slugger = smart_slugify(full_name, lower_case=True)
                shopper = Shopper.objects.create(
                    user = this_user,
                    email = form.cleaned_data['email'],
                    first_name = form.cleaned_data['first_name'],
                    last_name = form.cleaned_data['last_name'],
                    subscribed = form.cleaned_data['subscribed'],
                    slug = slugger,     
                )
            
            # create an address based on the info they provided         
            address = Address.objects.create(
                owner = shopper,
                house_name_number = form.cleaned_data['house_name_number'],
                address_line_1 = form.cleaned_data['address_line_1'],
                address_line_2 = form.cleaned_data['address_line_2'],
                town_city = form.cleaned_data['town_city'],
                postcode = form.cleaned_data['postcode'],
                country = "CHINA",
            )
            
            # create an order object
            basket_items = BasketItem.objects.filter(basket=basket)
            order = Order.objects.create(
                is_confirmed_by_user = True,
                date_confirmed = datetime.now(),
                address = address,
                owner = shopper,
                status = Order.STATUS_CREATED_NOT_PAID,
                invoice_id = "TEMP"
            )
            
            # add the items to the order
            for item in basket_items:
                order.items.add(item)
                order.save()

            # give the order a unique ID
            order.invoice_id = "TEA-00%s" % (order.id)
            order.save()

            request.session['ORDER_ID'] = order.invoice_id  
            
            # finally, we'll log the user in secretly (they don't even know it!)
            from django.contrib.auth import load_backend, login
            for backend in settings.AUTHENTICATION_BACKENDS:
                if this_user == load_backend(backend).get_user(this_user.pk):
                    this_user.backend = backend
            if hasattr(this_user, 'backend'):
                login(request, this_user)
                         
            return HttpResponseRedirect('/order/confirm') 
        
        # if the form has errors...
        else:
             # load their data if they already tried to submit the form and failed.
             email = request.POST['email']
             house_name_number = request.POST['house_name_number']
             address_line_1 = request.POST['address_line_1']
             address_line_2 = request.POST['address_line_2']
             town_city = request.POST['town_city']
             postcode = request.POST['postcode']
             first_name = request.POST['first_name']
             last_name = request.POST['last_name']

    confirm_form = OrderStepOneForm() 

    return render(request, 'shop/forms/order_step_one.html', locals())
 
 
# the view for 'logging out' if you're logged in with the wrong account   
def not_you(request):

	# remember the user's basket, otherwise they 'logout' but lose their own basket.
    this_user = request.user
    basket = Basket.objects.get(id=request.session['BASKET_ID'])
    
    # log the user out
    from django.contrib.auth import load_backend, logout
    for backend in settings.AUTHENTICATION_BACKENDS:
        if this_user == load_backend(backend).get_user(this_user.pk):
            this_user.backend = backend
    if hasattr(this_user, 'backend'):
        logout(request)
        # re-add the basket cookie so they don't lose their items
        request.session['BASKET_ID'] = basket.id
    
    # now they can return to the usual Step 1 of the form    
    return HttpResponseRedirect('/order/step-one/')    
    
    
    
# the view for the order step 2 - confirming your order
def order_confirm(request):
    shopper = get_object_or_404(Shopper, user=request.user)
    basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    order = Order.objects.get(invoice_id=request.session['ORDER_ID'])
    order_items = BasketItem.objects.filter(basket=basket)
    total_price = 0
    for item in order_items:
        price = item.quantity * item.item.price
        total_price += price
    
    if total_price > 50:
        postage_discount = True
    else: 
        total_price += 3
        
    if request.method == 'POST': 
        form = OrderCheckDetailsForm(request.POST)
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        basket.delete()
        new_basket = Basket.objects.create(owner=shopper, date_modified=datetime.now())
        request.session['BASKET_ID'] = new_basket.id
        
        return False
        
        
    else:
        form = PayPalPaymentsForm()

    return render(request, 'shop/forms/order_confirm.html', locals())
   
    
    
    
def order_complete(request):
    # the user should be logged in here, so we'll find their Shopper object
    # or redirect them to home if they're not logged in
    try:
        shopper = get_object_or_404(Shopper, user=request.user)
    except:
        shopper = None
    
    try:
        order = get_object_or_404(Order, invoice_id=request.session['ORDER_ID'])
    except:
        pass
        
    # this line should reset the basket cookie. basically, if 
    # the user ends up here, they need to have a new basket
    request.session['BASKET_ID'] = None
    
    if request.method == 'POST':
        form = SubmitTwitterForm(request.POST)
        
        if form.is_valid():
            twitter_username = form.cleaned_data['twitter_username']

            # save the shopper's twitter_username to their profile
            shopper.twitter_username = twitter_username
            shopper.save()
            
            if shopper.get_orders() is not None:
                # create a tweet
                tweet =  render_to_string('shop/emails/text/tweet.txt', {'twitter_username': twitter_username})
            
                # tweet a message to them to say thanks for ordering!
                twitter_post(tweet)            
            else:
                pass      
    
            return render(request, 'shop/order_complete.html', locals())
            
     
    else: 
        form = SubmitTwitterForm()

    return render(request, "shop/order_complete.html", locals())


# the user can choose to not have their stuff tweeted
def turn_off_twitter(request, id):
    try:
        shopper = get_object_or_404(Shopper, pk=id)
    except:
        pass
    
    shopper.twitter_username = None
    shopper.save()
    return HttpResponseRedirect('/order/complete/')

# handles the review/testimonial view
def review_tea(request, slug):
    tea = get_object_or_404(Product, slug=slug)
    other_reviews = Review.objects.filter(product=tea, is_published=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            words = form.cleaned_data['text'] 
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            review = Review.objects.create(
                text=words,
                product=tea,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            
            body = "%s %s just posted a review of %s" % (first_name, last_name, tea.name)              
            subject_line = "New Review Posted - %s" % tea.name 
            email_sender = settings.SITE_EMAIL
            recipient = settings.SITE_EMAIL
      
            send_mail(
                subject_line, 
                body, 
                email_sender,
                [recipient], 
                fail_silently=False
            )
            
            
            
            return HttpResponseRedirect('/review/thanks')
        
    else:
        form = ReviewForm()
    return render(request, "shop/forms/review_form.html", locals())

def send_review_email(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # create and send an email to the user to say thanks.
    
    subject = "christmastea.com - how to brew your tea"
    from_email = settings.SITE_EMAIL
    to_email = order.owner.email
    
    text_content = render_to_string('shop/emails/text/review_email.txt', {
        'shopper': order.owner, 
        'items': order.items.all(),
        }
    )
    
    html_content = render_to_string('shop/emails/html/html_review_email.html', {
        'items': order.items.all(),
        'shopper': order.owner,
        'subject': subject,
    })
    

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
    order.review_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')   


# view for the shipping page
def shipping(request):
    try:
        if request.session['MESSAGE'] == "1":
            message = True
            request.session['MESSAGE'] = ""
    except:
        pass 
        
    if request.method == 'POST':
        form = NotifyForm(request.POST)
        if form.is_valid():
            
            creation_args = {
                'email': form.cleaned_data['email'],          
            }
            
            Notify.objects.create(**creation_args)
            
            url = reverse('shipping')
            request.session['MESSAGE'] = "1"
            return HttpResponseRedirect(url)
        
    else:
        form = NotifyForm()
        
    return render(request, "shop/forms/shipping.html", locals())
            

# view for the photo wall
def reviews(request):
    reviews = Review.objects.filter(is_published=True)[:6]
    photos = Photo.objects.filter(published=True).order_by('-id')[:10]
    
    return render(request, 'shop/reviews.html', locals())


# view for a user's "I'm a tea lover" page
def tea_lover(request, slug):
    tea_lover = get_object_or_404(Shopper, slug=slug)
    
    return render(request, 'shop/tea_lover.html', locals())
 
 
 
# view for the tell_a_friend form      
def tell_a_friend(request):
        
    if request.method == 'POST':
        form = TellAFriendForm(request.POST)
        if form.is_valid():
            
            # get cleaned data from form submission
            sender = form.cleaned_data['sender']
            message = form.cleaned_data['message']
            recipient = form.cleaned_data['recipient']
            
            # create email
            if message:
                body = render_to_string('shop/emails/text/custom_tell_friend.txt', {'message': message})
            else:
                body = render_to_string('shop/emails/text/tell_friend.txt', {'sender': sender})
            
            subject_line = "%s wants you to know about christmastea.com" % sender
                
            send_mail(
                          subject_line, 
                          body, 
                          sender,
                          [recipient], 
                          fail_silently=False
            )
            
            # create the referrer/referee objects
            try:
                referrer = get_object_or_404(Shopper, email=sender)
                referrer.number_referred += 1
                referrer.save()
            except:
                referrer = Shopper.objects.create(email=sender, number_referred=1)
                referrer.save()
            
            referee = Referee.objects.create(
                    email=recipient,
                    referred_by=referrer,
                    )
            referee.save()
                 
            
            
            message = "We've sent an email to %s letting them know about christmastea.com - thanks for your help!" % referee.email
            # then send them back to the tell a friend page
            return render(request, "shop/forms/tell_a_friend.html", locals())

        else:
            if form.non_field_errors():
                non_field_errors = form.non_field_errors()
            else:
                errors = form.errors
             
    else:
        form = TellAFriendForm()
    return render(request, 'shop/forms/tell_a_friend.html', locals())

# view for my private admin pages
def admin_stuff(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    
    # get the stats
    products = Product.objects.all()
    total_baskets = Basket.objects.all()
    total_orders = Order.objects.all()
    total_shoppers = Shopper.objects.all()
    published_photos = Photo.objects.filter(published=True)
    unpublished_photos = Photo.objects.filter(published=False)
    orders = Order.objects.all().filter(is_giveaway=False).order_by('-date_confirmed')
    giveaways = Order.objects.all().filter(is_giveaway=True).order_by('-date_confirmed')
    
    # work out how many sales we've made
    total_sales = 0
    for order in orders:
        total_sales += order.get_amount() 
    
    # make the nice lists for paid/unpaid orders
    all_orders = []    
    for order in orders:
        if order.status == Order.STATUS_CREATED_NOT_PAID:
            pass
        else:
            all_orders.append((order, order.items.all())) 
    
    all_giveaways = []
    for order in giveaways:
        all_giveaways.append((order, order.items.all()))

    return render(request, "shop/admin_base.html", locals())

#specific shopper view in admin-stuff
def admin_shopper(request, id):
    shopper = get_object_or_404(Shopper, pk=id)
    return render(request, 'shop/admin_shopper.html', locals())

# specific order view in admin-stuff
def admin_order(request, id):
    order = get_object_or_404(Order, pk=id)
    return render(request, 'shop/admin_order.html', locals())

# function for changing order status from admin-stuff
def ship_it(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    
    order = get_object_or_404(Order, pk=id)
    order.status = Order.STATUS_SHIPPED
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')

# function for sending the 'send sample to friend' email
def send_sampler_email(request, id):
    order = get_object_or_404(Order, pk=id)
    shopper = order.owner
    if order.sampler_email_sent:
        return False

    from_email = settings.SITE_EMAIL
    to_email = shopper.email
    subject = "Give a tea gift to a friend, courtesy of the Min River Tea Farm"
            
    # create email
    text_content = render_to_string('shop/emails/text/send_sample_to_friend_email.txt', {'shopper': shopper})
    html_content = render_to_string('shop/emails/html/send_sample_to_friend.html', {
    	'shopper': shopper,
    	'subject': subject,
    })
    
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    
    order.sampler_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')
    
    
    
    
    
    
    
    
    