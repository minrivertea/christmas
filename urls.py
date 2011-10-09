from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.views.generic.simple import direct_to_template
from shop.models import Product, Page
from shop.views import page, sub_page, sub_sub_page, sub_sub_sub_page

# admin urls
from django.contrib import admin
admin.autodiscover()

# for the sitemaps
products = {
    'queryset': Product.objects.filter(is_active=True),
}

pages = {
    'queryset': Page.objects.all(),	
}

sitemaps = {
    'pages': GenericSitemap(products, priority=0.6),
    'products': GenericSitemap(products, priority=0.6),
}

# main URL patterns
urlpatterns = patterns('',
    (r'^', include('christmas.shop.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^humans\.txt$', direct_to_template, {'template': 'humans.txt', 'mimetype': 'text/plain'}),
    (r'^products\.xml$', direct_to_template, {'template': 'products.xml', 'mimetype': 'text/xml'}),
    (r'^400/$', direct_to_template, {'template': '404.html'}),  
    (r'^comments/', include('django.contrib.comments.urls')), 
    url(r'^(?P<slug>[\w-]+)/$', page, name="page"),
    url(r'^(?P<slug>[\w-]+)/(?P<sub_slug>[\w-]+)/$', sub_page, name="sub_page"),
    url(r'^(?P<slug>[\w-]+)/(?P<sub_slug>[\w-]+)/(?P<sub_sub_slug>[\w-]+)/$', sub_sub_page, name="sub_sub_page"),
    url(r'^(?P<slug>[\w-]+)/(?P<sub_slug>[\w-]+)/(?P<sub_sub_slug>[\w-]+)/(?P<sub_sub_sub_slug>[\w-]+)/$', 
        sub_sub_sub_page, name="sub_sub_sub_page"),  
)


# for the development server static files
urlpatterns += patterns('',

    # CSS, Javascript and IMages
    (r'^photos/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/photos',
        'show_indexes': settings.DEBUG}),
    (r'^images/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/images',
        'show_indexes': settings.DEBUG}),
    (r'^cache/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/cache',
        'show_indexes': settings.DEBUG}),
    (r'^thumbs/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/thumbs',
        'show_indexes': settings.DEBUG}),
    (r'^css/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/css',
        'show_indexes': settings.DEBUG}),
    # for the fontface CSS trick to work
    (r'^fonts/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/fonts',
        'show_indexes': settings.DEBUG}),
    (r'^js/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/js',
        'show_indexes': settings.DEBUG}),
)
