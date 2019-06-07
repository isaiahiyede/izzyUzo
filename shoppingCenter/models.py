from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Sum
# from model_utils import FieldTracker
from shipping.models import DomesticPackage, ShippingPackage
from service_provider.models import MarketingMember
#from general.models import AddressBook

# Create your models here.


class ShoppingCategory(models.Model):
	name 					 = models.CharField(max_length=250, null=True, blank=True)
	desc 					 = models.CharField(max_length=250, null=True, blank=True)
	created_by 			     = models.CharField(max_length=50, null=True, blank=True)

	class Meta:
		verbose_name_plural ='ShoppingCategory'

	def __unicode__(self):
		return self.name


class ShoppingOrder(models.Model):
	user  					= models.OneToOneField(User, null=True, blank=True)
	tracking_number         = models.CharField(max_length = 50, null=True)
	quantity        		= models.IntegerField(default=1)
	#shipping_to             = models.OneToOneField(AddressBook, null=True, blank=True)
	shipping_cost           = models.FloatField(default = 0)

	class Meta:
		verbose_name_plural = 'ShoppingOrder'

	def __unicode__(self):
		return self.tracking_number


class ShoppingItem(models.Model):
	created_by 			     = models.CharField(max_length=50, null=True, blank=True)
	name 					 = models.CharField(max_length=150, null=True, blank=True)
	desc 					 = models.CharField(max_length=250, null=True, blank=True)
	weight 					 = models.DecimalField(max_digits = 15, decimal_places = 1)
	shoppingItem_image       = models.ImageField(upload_to = 'shoppingItem_image/%Y/%m/%d', null=True, blank=True)
	price 					 = models.FloatField(default = 0)
	category 				 = models.ForeignKey(ShoppingCategory, null=True, blank=True)
	shopping_order           = models.ForeignKey(ShoppingOrder, null=True, blank=True)
	created_on               = models.DateTimeField(auto_now_add = True)

	class Meta:
		verbose_name_plural  = 'ShoppingItem'
		ordering = ['created_on']

	def __unicode__(self):
		return self.name



class UserOrder(models.Model):
	client       = models.ForeignKey(User, null=True)
	order_number = models.CharField(max_length = 12)
	payable      = models.DecimalField(max_digits=15, decimal_places=2, null=True)
	local_pkg    = models.ForeignKey(DomesticPackage, null=True,blank=True)
	intl_pkg     = models.ForeignKey(ShippingPackage, null=True,blank=True)
	created_on   = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.order_number
	
	def all_items(self):
		return self.addinventory_set.all()
	



class Cart(models.Model):
    client         = models.ForeignKey(User,null=True,blank=True)
    # docfile      = models.ImageField(upload_to='ZeroAC/static/images/document/%Y%m%d', blank=True,null=True)
    # description  = models.CharField(max_length = 2500)
    # price        = models.DecimalField(max_digits=10, decimal_places=2)
    quantity       = models.PositiveIntegerField(default=1)
    # details      = models.CharField(max_length = 2500, blank=True, null=True)
    item           = models.ForeignKey('AddInventory',null=True,blank=True)
    ordered        = models.BooleanField(default=False)
    shipping_items = models.ForeignKey(DomesticPackage,blank=True,null=True)
    #created_on    = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.client.username
    
    def item_count(self):
        return self.addinventory_set.all().count()

    def total(self):
        return self.item.price * self.quantity
    
    def total_weight(self):
        return self.item.weight * self.quantity
    
    # def get_qty(self):
    #     return self.quantity



class Category(models.Model):
    marketer = models.ForeignKey(MarketingMember,null=True,blank=True)
    cat_name = models.CharField(max_length = 2500,null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.cat_name
  

  
class SubCategory(models.Model):
    sub_cat      = models.ForeignKey(Category,null=True,blank=True)
    sub_cat_name = models.CharField(max_length = 2500,null=True, blank=True)

    class Meta:
        verbose_name_plural = "SubCategories"

    def __str__(self):
        return self.sub_cat_name
  
  
class AddInventory(models.Model):
    marketer       = models.ForeignKey(MarketingMember,null=True,blank=True)
    sub_sub_cat    = models.ForeignKey(SubCategory,null=True,blank=True)
    item_image     = models.ImageField(upload_to='ZeAC/static/images/document/%Y%m%d', blank=True)
    title          = models.CharField(max_length = 255,null=True,blank=True, unique=True)
    description    = models.CharField(max_length = 2500,null=True, blank=True)
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    colour         = models.CharField(max_length = 25,null=True,blank=True)
    brand          = models.CharField(max_length = 100,null=True,blank=True)
    size           = models.PositiveIntegerField(default=0)
    weight         = models.FloatField(default= 0.1)
    unit           = models.CharField(max_length = 5,default = "kg")
    quantity       = models.PositiveIntegerField(default=0)
    sold           = models.PositiveIntegerField(default=0)
    specifications = models.CharField(max_length = 2500,null=True,blank=True)
    item_type      = models.CharField(max_length=20, default="inventory")
    created_on     = models.DateTimeField(auto_now_add=True)
    user_order     = models.ForeignKey(UserOrder,null=True,blank=True)
    class Meta:
        verbose_name_plural = "Inventory"

    def item_remaining(self):
        return self.quantity - self.sold

    def __str__(self):
        return self.title


class Order(models.Model):
    client = models.ForeignKey(User, null=True)
    order_number = models.CharField(max_length = 12)
    payable = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    email = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    item = models.ForeignKey(AddInventory, null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.order_number






