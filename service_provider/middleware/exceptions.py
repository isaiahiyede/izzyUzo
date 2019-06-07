from django.shortcuts import render
from service_provider.exceptions.custom import NotFound

class ExceptionMiddleware(object):
    
    def process_exception(self, request, exception):
        if type(exception) == NotFound:
            return render(request, exception.template)
        
        return None