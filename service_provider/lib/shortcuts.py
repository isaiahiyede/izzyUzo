
#source: https://chriskief.com/2012/12/28/django-get_object_or_404-replacement-get_object_or_template/

from django.shortcuts import _get_queryset
from service_provider.exceptions.custom import NotFound

def get_object_or_template(klass, template, *args, **kwargs):
    # replacement for django.shortcuts.get_object_or_404()
    # allows a template to be supplied instead of a 404
    
    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.
    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """

    queryset = _get_queryset(klass)
    
    try:
        return queryset.get(*args, **kwargs)
    except:
        print template
        raise NotFound(template)