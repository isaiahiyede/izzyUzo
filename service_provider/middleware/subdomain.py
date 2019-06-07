from service_provider.models import MarketingMember
from service_provider.lib.shortcuts import get_object_or_template
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponse

class SubDomainMiddleware(object):

    # def process_request(self, request):
    #     scheme = "http" if not request.is_secure() else "https"
    #     path = request.get_full_path()
    #     url = request.META.get('HTTP_HOST') or request.meta.get('SERVER_NAME')

    def process_request(self, request):
        domain = request.META.get('HTTP_HOST') or request.META.get('SERVER_NAME')
        print 'domain: ',domain

        resolved_url_name = resolve(request.path).url_name
        print 'resolved_url_name: ',resolved_url_name
        #next_path = request.get_full_path().split('=')[-1]
        #resolved_namespace = resolve(next_path).namespace
        resolved_namespace = resolve(request.path).namespace
        print 'resolved_namespace: ',resolved_namespace
        if domain in ['www.sokohali.com', 'sokohali.com', 'sokohali.dev:9003'] or '127.0.0.1' in domain or '192' in domain or 'localhost' in domain or '172' in domain:
            if resolved_namespace in ['admin']:
                return None
            else:
                if resolved_url_name in ['marketer_homepage']:
                    # return render(request, 'marketingmember_index.html')
                    return None
                elif resolved_url_name == 'homepage':
                    return render(request, 'sokohali/sokohali_homepage.html')
                # elif resolved_url_name == "export_landing_page":
                #     if '127.0.0.1' not in domain:
                #         return render(request, "404.html")
                else:
                    return None
        else:
            try:
                '''a subdomain request'''

                '''deny django admin view for marketing members'''
                # if resolved_namespace in ['admin']:
                #     return render(request, '404.html')

                url_split = domain.split('.')
                # print "url_split:",url_split
                len_url_split = len(url_split)
                # print "len_url_split:",len_url_split

                if len_url_split == 3:
                    '''for xxx.sokohali.com'''
                    storefront_name = url_split[-2]
                elif len_url_split == 4:
                    storefront_name = url_split[-3]
                else:
                    '''for sokohali.com'''
                    storefront_name = url_split[-2]
                #if len(url_split) > 2:

                #storefront_name = url_split[-2]
                print 'storefront_name: ',storefront_name

                marketing_member = MarketingMember.objects.get(storefront_name = storefront_name)
                if marketing_member.logo:
                    request.marketer_logo_url = marketing_member.logo.url
                '''add marketing_member to request'''
                request.marketing_member     = marketing_member
                request.subdomain_name       = storefront_name
                request.storefront_name      = marketing_member.storefront_name
                request.storefront_logo_url  = marketing_member.logo.url
                request.storefront_email     = marketing_member.email


            except Exception as e:
                # print 'middleware subdomain :e',e
                '''to avoid unmatched urls; especially get request'''
                #print 'type of e: ',e.__class__.__name__
                if e.__class__.__name__ == "DoesNotExist":#"Http404":
                     return render(request, 'shop_not_available.html')
