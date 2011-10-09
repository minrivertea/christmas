from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views


urlpatterns = patterns('',

    url(r'^$', views.index, name="home"),
    url(r'^admin-stuff/$', views.admin_stuff, name="admin_stuff"),
    url(r'^admin-stuff/send-review-email/(\w+)$', views.send_review_email, name="send_review_email"),
    url(r'^admin-stuff/ship-it/(\w+)$', views.ship_it, name="ship_it"),
    url(r'^admin-stuff/shopper/(\w+)$', views.admin_shopper, name="admin_shopper"),
    url(r'^admin-stuff/order/(\w+)$', views.admin_order, name="admin_order"),
    url(r'^admin-stuff/send-sampler-email/(\w+)/$', views.send_sampler_email, name="send_sampler_email"),
    url(r'^contact-us/$', views.contact_us, name="contact_us"),
    url(r'^sale/$', views.sale, name="sale"),
    url(r'^cards/$', views.products, name="products"),
    url(r'^cards/(?P<slug>[\w-]+)/review/$', views.review_tea, name="review_tea"),
    url(r'^cards/(?P<slug>[\w-]+)/$', views.product_view, name="product_view"),
    url(r'^basket/$', views.basket, name="basket"),
    url(r'^basket/add/(\w+)$', views.add_to_basket, name="add_to_basket"),
    url(r'^basket/reduce/(\w+)$', views.reduce_quantity, name="reduce_quantity"),
    url(r'^basket/increase/(\w+)$', views.increase_quantity, name="increase_quantity"),
    url(r'^basket/remove/(\w+)$', views.remove_from_basket, name="remove_from_basket"),
    url(r'^order/step-one/$', views.order_step_one, name="order_step_one"),
    url(r'^order/confirm/$', views.order_confirm, name="order_confirm"),
    url(r'^order/complete/$', views.order_complete, name="order_complete"),
    url(r'^order/complete/turn-off-twitter/(\w+)$', views.turn_off_twitter, name="turn_off_twitter"),    
    url(r'^reviews/$', views.reviews, name="reviews"),
    url(r'^review/thanks/$', direct_to_template, {'template': 'shop/review_thanks.html',}),
    url(r'^tea-lover/(?P<slug>[\w-]+)/$', views.tea_lover, name="tea_lover"),
    url(r'^tell-a-friend/$', views.tell_a_friend, name="tell_a_friend"),
    url(r'^not-me/$', views.not_you, name="not_you"),
    url(r'^shipping/$', views.shipping, name="shipping"),

)

