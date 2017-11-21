from django import forms
from rango.models import Page, Category


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # inline class to provide additional information
    class Meta:
        # provide association between the ModelForm and a model
        model = Category
        fields = ('name',)


class PageForms(forms.ModelForm):
    title = forms.CharField(max_length=128,
                            help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,
                         help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        """ What fields do we want to include in our form?
            This way we don't need every field in the model present.
            some fields may allow NULL values, so we may not want to include them.
            Here, we are hiding the foreign key.
            we can either exclude the category field from the form,
            or specify the fields to include (i.e. not include the category field)"""
        model = Page
        exclude = ('category',)
        # fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data  # contains form data
        url = cleaned_data.get('url')  # .get handles KeyError!!!

        # prepend 'http://' before none empty urls
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url
            # must return reference to cleaned data
            return cleaned_data
