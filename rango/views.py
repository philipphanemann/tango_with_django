from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page


def index(request):

    return HttpResponse('Rango says hey there partner')
# Create your views here.


def index2(request):
    """ index of the rango app

    Query the database for a list of ALL categories currently stored.
    Order the categories by no. likes in descending order.
    Retrieve the top 5 only - or all if less than 5.
    Place the list in our context_dict dictionary
    that will be passed to the template engine."""

    # using ('-likes') for descending is 50 % faster than ('likes').reverse()
    category_list = Category.objects.order_by('-likes')[:5]
    top_5_pages = Page.objects.order_by('views')[:5]
    context_dict = {'categories': category_list, 'pages': top_5_pages}
    # Render the response and send it back!

    return render(request, 'rango/index.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # get category instance with slug else, a DoesNotExist exception is raised.
        category = Category.objects.get(slug=category_name_slug)

        # get list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        context_dict['pages'] = pages
        # add the category to context dictionary.
        # we'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # do nothing, the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request, 'rango/category.html', context_dict)
