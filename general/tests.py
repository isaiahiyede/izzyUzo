
#python manage.py dumpdata > zaposta_data.json
#python manage.py dumpdata --exclude contenttypes > zaposta-fixture-1.json


from django.test import TestCase
from .keywordShippingWeight import suggestedWeightAndInfo


class TestShippingKeywordManager(TestCase):
    
    fixtures = ['/Users/zaposta/Dropbox/Dropbox/Work-Related/WebApps/CAApps/zaposta-fixture-1.json']
    #fixtures = ['zaposta-fixture-1.json']

    def confirm_keyword(self):
        products = [{'description': 'Trysta Fringe-Trim Dress', 'quantity': 1, 'listed_price_D': 200, 'country': 'us'}]
        suggestedWeight, matchingKeywords_info = suggestedWeightAndInfo(items)
        print "suggestedWeight: ", suggestedWeight
        print "matchingKeywords_info: ", matchingKeywords_info
        return True

# from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.firefox.webdriver import WebDriver
# 
# class MySeleniumTests(StaticLiveServerTestCase):
#     #fixtures = ['/Users/zaposta/Dropbox/Dropbox/Work-Related/WebApps/CAApps/zaposta-fixture-1.json']
#     fixtures = ['zaposta-fixture-1.json']
# 
#     @classmethod
#     def setUpClass(cls):
#         super(MySeleniumTests, cls).setUpClass()
#         cls.selenium = WebDriver()
# 
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super(MySeleniumTests, cls).tearDownClass()
# 
#     def test_login(self):
#         self.selenium.get('%s%s' % (self.live_server_url, '/user/login/'))
#         #username_input = self.selenium.find_element_by_name("username_email")
#         username_input = self.selenium.find_element_by_id("id_username_email")
#         username_input.send_keys('ajirapsy')
#         #password_input = self.selenium.find_element_by_name("password")
#         password_input = self.selenium.find_element_by_id("id_password")
#         password_input.send_keys('circuitatl')
#         self.selenium.find_element_by_id("login_form").submit()
#         #self.selenium.find_element_by_xpath('//button[@value="Submit"]').click()
#         #self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
#         