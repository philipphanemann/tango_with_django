from django import template
from rango.models import Category

register = template.Library()


@register.inclusion_tag('rango/categories_sidebar.html')
def get_category_list(category=None):
    return {'categories': Category.objects.all(),
            'act_category': category}
