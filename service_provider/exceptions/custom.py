


class NotFound(Exception):
    def __init__(self, template):
    
        #call the base class constructor
        Exception.__init__(self, 'Record not found')
        
        self.template = template
