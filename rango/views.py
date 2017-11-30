from datetime import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm


def get_server_side_cookie(request, cookie, default=None):
    """ return server side cookie if exists else default """
    val = request.session.get(cookie)
    if not val:
        val = default
    return val


def visitor_cookie_handler(request):
    """ helper function to get the number of visits to the site

    Server side cookies are encouraged.
    The code for client side cookies is in chapter 10.5
    """

    visits = int(get_server_side_cookie(request, 'visits', default=1))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        # TODO: setting visits might not be necessary
        visits = 1
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def index(request):
    """ index of the rango app

    Query the database for a list of ALL categories currently stored.
    Order the categories by no. likes in descending order.
    Retrieve the top 5 only - or all if less than 5.
    Place the list in our context_dict dictionary
    that will be passed to the template engine.

    --- render(request, template, ...) is pretty nice ---
    1. there is a lot of information coming with the user request
    2. the template for displaying is passed
    3. additional information can be passed"""

    # using ('-likes') for descending is 50 % faster than ('likes').reverse()
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    top_5_pages = Page.objects.order_by('views')[:5]
    context_dict = {'categories': category_list, 'pages': top_5_pages}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context=context_dict)

    # return response with updated cookie information to the user
    return response


def about(request):
    if request.session.test_cookie_worked():
        print('TEST COOKIE WORKDED!')
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


@login_required
def add_category(request):

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database and return category object.
            form.save(commit=True)
            # Now that the category is saved, we could give a confirmation message
            # But since the most recent category added is on the index page,
            # we can direct the user back to the index page.
            return index(request)
        else:
            # The supplied form contained errors - print them to the terminal
            print(form.errors)
        # Will handle the bad form, new form, or no form supplied cases.
        # Render the form with error messages (if any)
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    """ add a page to an existing category """
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid() and category:
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()
            return show_category(request, category_name_slug)
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    """ return True if the registration was successful, else false

    1. deal with two forms 'user' and 'profile' and with the picture upload
    2. link user_form information with profile_form information"""

    registered = False
    # process/grap form data if 'POST' request
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # save to database
            user = user_form.save()
            # hash password and update user object
            user.set_password(user.password)
            user.save()
            # user attribute is not yet set at profile_form.
            # We commit/save it later to the database
            profile = profile_form.save(commit=False)
            profile.user = user
            # save profile picture if provided
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # render blank form, ready for input - use two ModelForm instances
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,
                  'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    """ obtain user information via POST request

    a)  make use of request.POST.get('<variable>') to circumvent possible
        KeyError via request.POST['<variable>'] access
    b)  check for validity of username and password
        if valid and active user --> send back to 'index'
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                HttpResponse('Your Rango account is disabled.')
        else:
            print('Invalid login details: {0}, {1}'.format(username, password))
            return HttpResponse('Invalid login details supplied')
    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required
def user_logout(request):
    """ logout and redirect """
    logout(request)
    return HttpResponseRedirect(reverse('index'))
