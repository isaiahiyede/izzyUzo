from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib import messages
from django.views.generic import TemplateView
from general.models import UserAccount
from general.forms import AddressActivationForm, EditProfileForm, AddressActivationForm1, AddressActivationForm2, \
    AddressActivationForm3
from django.contrib.auth.models import User
from general.encryption import value_encryption, value_decryption
from general.custom_functions import marketing_member, get_marketing_member_user, generate_suite_no
# from bvn_validation import
from general.custom_functions import sokohali_sendmail
from shipping.models import ShippingItem, ShippingPackage


@login_required()
def redirect_to_address_activation(request):
    # messages.info(request, "Your account has to be verified before you can become a Sokohali Partner Affiliate.")
    username = request.user.username
    return redirect(reverse("general:address_activation", args=[username]))


@login_required(login_url='/volk/login/')
def redirect_to_address_activation_new(request):
    # messages.info(request, "Your account has to be verified before you can become a Sokohali Partner Affiliate.")
    username = request.user.username
    return redirect(reverse("general:address_activation_new", args=[username]))


def is_bvn_used(request, bvn):
    encrypted_val = value_encryption(bvn)
    mm = marketing_member(request)
    return UserAccount.objects.filter(marketer=mm, bvn_no=encrypted_val).exists()


@login_required
def address_activation(request, username):
    if request.user.is_staff:
        username = username
    else:
        username = request.user
    user = get_marketing_member_user(request, username)

    if user.useraccount.address_activation_completed:
        return redirect(reverse("general:profile", args=[username]))

    if request.method == "POST":
        # form = AddressActivationForm()

        ''' start: Block of code commented by isaiah to remove bvn validation on 22nd/june/2017 '''

        # if request.POST["country"] == "Nigeria":
        #      bvn_no = request.POST.get("bvn_no", "")
        #      #for bvn
        #      if bvn_no != "" :
        #      #if bvn_no != "" and bank_account_no == "":
        #           if not is_bvn_used(request,bvn_no):
        #                form = AddressActivationForm1(request.POST, request.FILES, instance = user.useraccount)
        #                if form.is_valid():
        #                     #form.save()
        #                     formNG = form.save(commit = False)
        #                     formNG.address_activation_completed = True
        #                     formNG.address_act_completed_date = timezone.now()
        #                     formNG.address_activation = True
        #                     #encrypt bank account number/bvn no
        #                     formNG.bvn_no = value_encryption(bvn_no)
        #                     formNG.suite_no = generate_suite_no()
        #                     formNG.save()
        #                     user = formNG.user
        #                     user = User.objects.get(pk=user.id)
        #                     user.first_name = formNG.first_name
        #                     user.last_name = formNG.last_name
        #                     user.save()
        #                     print user.first_name
        #                     text = 'email/address_activation.txt'
        #                     try:
        #                          sokohali_sendmail(request, user, "Account Verification", text, None)
        #                     except:
        #                          pass
        #                     return redirect(reverse("general:profile", args = [username]))
        #                else:
        #                     print form.errors
        #           else:
        #                messages.info(request, "Error! This BVN number is already in use.")
        #                return redirect(request.META.get("HTTP_REFERER", '/'))
        #      else:
        #           messages.info(request, "Error! Form is incomplete. Please complete all fields.")
        #           return redirect(request.META.get("HTTP_REFERER", '/'))
        #      #for bank account
        #      # elif bvn_no == "" and bank_account_no != "":
        #      #      form = AddressActivationForm2(request.POST, request.FILES, instance = user.useraccount)
        #      # # #for bank account
        #      # if bank_account_no != "":
        #      #      form = AddressActivationForm2(request.POST, request.FILES, instance = user.useraccount)
        # else:
        #      form = AddressActivationForm3(request.POST, request.FILES, instance = user.useraccount)

        ''' end: Block of code commented by isaiah to remove bvn validation on 22nd/june/2017 '''

        form = AddressActivationForm3(request.POST, request.FILES, instance=user.useraccount)
        if form.is_valid():
            # form.save()
            others = form.save(commit=False)
            others.address_activation_completed = True
            others.address_act_completed_date = timezone.now()
            others.bvn_no = ""
            others.suite_no = generate_suite_no()
            others.save()
            user = others.user
            user = User.objects.get(pk=user.id)
            user.first_name = others.first_name
            user.save()
            print user.first_name
            # text = 'email/address_activation.txt'
            # try:
            #     sokohali_sendmail(request, user, "Account Verification", text, None)
            # except:
            #     pass
            return redirect(reverse("general:profile", args=[username]))

            # if user.useraccount.country == 'Nigeria':
            #    address = AddressBook.objects.create(user = user, title = form.cleaned_data['title'], full_name = user.get_full_name(), \
            #                          address = form.cleaned_data['address'], city = form.cleaned_data['city'], state = form.cleaned_data['state'],
            #    country = form.cleaned_data['country'], telephone = user.useraccount.telephone)
            #
            # return redirect ('/shipping/account/')
            # return redirect(reverse("userAccount.shipping_views.account"))

            # if user wants to become a reseller, proceed to application page
            # if request.GET.has_key('source_action'):
            #      return redirect(reverse("reseller:reseller_application"))
            # else:
            #      return redirect(reverse("general:profile", args = [username]))
        # print form.errors
    else:
        form = AddressActivationForm(instance=user.useraccount)
        # print form
    return render(request, 'user_profile/address_activation.html', {'form': form, 'user': user},
                  )


@login_required(login_url='/volk/login/')
def address_activation_new(request, username):
    if request.user.is_staff:
        username = username
    else:
        username = request.user
    user = get_marketing_member_user(request, username)

    if user.useraccount.address_activation_completed:
        return redirect(reverse("general:profile_volk", args=[username]))

    if request.method == "POST":
        # form = AddressActivationForm()

        ''' start: Block of code commented by isaiah to remove bvn validation on 22nd/june/2017 '''

        # if request.POST["country"] == "Nigeria":
        #      bvn_no = request.POST.get("bvn_no", "")
        #      #for bvn
        #      if bvn_no != "" :
        #      #if bvn_no != "" and bank_account_no == "":
        #           if not is_bvn_used(request,bvn_no):
        #                form = AddressActivationForm1(request.POST, request.FILES, instance = user.useraccount)
        #                if form.is_valid():
        #                     #form.save()
        #                     formNG = form.save(commit = False)
        #                     formNG.address_activation_completed = True
        #                     formNG.address_act_completed_date = timezone.now()
        #                     formNG.address_activation = True
        #                     #encrypt bank account number/bvn no
        #                     formNG.bvn_no = value_encryption(bvn_no)
        #                     formNG.suite_no = generate_suite_no()
        #                     formNG.save()
        #                     user = formNG.user
        #                     user = User.objects.get(pk=user.id)
        #                     user.first_name = formNG.first_name
        #                     user.last_name = formNG.last_name
        #                     user.save()
        #                     print user.first_name
        #                     text = 'email/address_activation.txt'
        #                     try:
        #                          sokohali_sendmail(request, user, "Account Verification", text, None)
        #                     except:
        #                          pass
        #                     return redirect(reverse("general:profile", args = [username]))
        #                else:
        #                     print form.errors
        #           else:
        #                messages.info(request, "Error! This BVN number is already in use.")
        #                return redirect(request.META.get("HTTP_REFERER", '/'))
        #      else:
        #           messages.info(request, "Error! Form is incomplete. Please complete all fields.")
        #           return redirect(request.META.get("HTTP_REFERER", '/'))
        #      #for bank account
        #      # elif bvn_no == "" and bank_account_no != "":
        #      #      form = AddressActivationForm2(request.POST, request.FILES, instance = user.useraccount)
        #      # # #for bank account
        #      # if bank_account_no != "":
        #      #      form = AddressActivationForm2(request.POST, request.FILES, instance = user.useraccount)
        # else:
        #      form = AddressActivationForm3(request.POST, request.FILES, instance = user.useraccount)

        ''' end: Block of code commented by isaiah to remove bvn validation on 22nd/june/2017 '''

        form = AddressActivationForm3(request.POST, request.FILES, instance=user.useraccount)
        if form.is_valid():
            # form.save()
            others = form.save(commit=False)
            others.address_activation_completed = True
            others.address_act_completed_date = timezone.now()
            others.bvn_no = ""
            others.suite_no = generate_suite_no()
            others.save()
            user = others.user
            user = User.objects.get(pk=user.id)
            user.first_name = others.first_name
            user.save()
            print user.first_name
            # text = 'email/address_activation.txt'
            # try:
            #     sokohali_sendmail(request, user, "Account Verification", text, None)
            # except:
            #     pass
            return redirect(reverse("general:profile_volk", args=[username]))

            # if user.useraccount.country == 'Nigeria':
            #    address = AddressBook.objects.create(user = user, title = form.cleaned_data['title'], full_name = user.get_full_name(), \
            #                          address = form.cleaned_data['address'], city = form.cleaned_data['city'], state = form.cleaned_data['state'],
            #    country = form.cleaned_data['country'], telephone = user.useraccount.telephone)
            #
            # return redirect ('/shipping/account/')
            # return redirect(reverse("userAccount.shipping_views.account"))

            # if user wants to become a reseller, proceed to application page
            # if request.GET.has_key('source_action'):
            #      return redirect(reverse("reseller:reseller_application"))
            # else:
            #      return redirect(reverse("general:profile", args = [username]))
        # print form.errors
    else:
        form = AddressActivationForm(instance=user.useraccount)
        # print form
    return render(request, 'user_profile/address_activation.html', {'form': form, 'user': user},
                  )


@login_required
def profile(request, username):
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    bvn_no = None
    if request.user.is_staff:
        username = username
    else:
        username = request.user
    mm = marketing_member(request)
    profile = get_object_or_404(UserAccount, user__username=username, marketer=mm)
    if profile.bvn_no != "":
        if profile.bvn_no[-1] == "=":
            bvn_no = value_decryption(profile.bvn_no)
        else:
            bvn_no = None

    # if profile.address_activation_completed:
    # address_string = OperatingCountry.objects.get(country = "uk").delivery_address
    # uk_shipping_address =  address_string %(" Suite No %s, " %profile.suite_no)
    #
    # address_string = OperatingCountry.objects.get(country = "us").delivery_address
    # us_shipping_address =  address_string %("%s" %profile.suite_no)
    #
    # #delivery_addresses = [uk_shipping_address]
    #
    # delivery_addresses = [us_shipping_address, uk_shipping_address]

    if mm.storefront_name == "volkmannexpress":
        return render(request, 'volkmann/profile_view.html', {'profile': profile, 'decrypt_bvn_no': bvn_no,
                                                              'count': count_items})  # 'delivery_addresses': delivery_addresses},
    else:
        return render(request, 'user_profile/profile.html', {'profile': profile, 'decrypt_bvn_no': bvn_no}
                      # 'delivery_addresses': delivery_addresses},
                      )
    # else:
    #   return redirect(reverse("general:address_activation", args = [username]))


@login_required
def edit_profile(request, username=None):
    # try:
    #    user = User.objects.get(username = username)
    # except User.DoesNotExist:
    #    raise Http404
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    mm = marketing_member(request)

    if request.user.is_authenticated():

        if username == "None":
            return redirect("/user/login/?next=" + reverse("general:edit_profile", args=[request.user.username]))
        username = request.user
        # user = get_object_or_404(User, username = username)
        user = get_marketing_member_user(request, username)

        if request.method == "POST":
            form = EditProfileForm()
            form = EditProfileForm(request.POST, request.FILES, instance=user.useraccount)
            if form.is_valid():
                # address_book = AddressBook.objects.filter(user = request.user)
                # for a in address_book:
                #    b = AddressBook(title = form.cleaned_data['title'],telephone   = form.cleaned_data['telephone'],\
                #                               address = form.cleaned_data['address'],city = form.cleaned_data['city'], postal_code = form.cleaned_data['postal_code'], state = form.cleaned_data['state'],\
                #                               country     = form.cleaned_data['country'])
                #    b.save()
                form.save()

                # update first and last name of the user
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                # if form.cleaned_data['country']:
                #    address = AddressBook.objects.filter(user = request.user)[:0]
                return redirect(reverse("general:profile", args=[username]))
            # print form.errors
        else:
            form = EditProfileForm(instance=user.useraccount)
        mm.storefront_name == "volkmannexpress"
        return render(request, 'volkmann/profile.html',
                          {'form': form, 'user_details': user, 'count_items': count_items})
            # return render(request, 'user_profile/edit_profile.html', {'form': form, 'user_details': user},

    else:
        return redirect("/user/login/?next=" + reverse("general:edit_profile", args=[None]))


@login_required(login_url='/volk/login/')
def profile_volk(request, username):
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    bvn_no = None
    if request.user.is_staff:
        username = username
    else:
        username = request.user
    mm = marketing_member(request)
    profile = get_object_or_404(UserAccount, user__username=username, marketer=mm)
    if profile.bvn_no != "":
        if profile.bvn_no[-1] == "=":
            bvn_no = value_decryption(profile.bvn_no)
        else:
            bvn_no = None

    # if profile.address_activation_completed:
    # address_string = OperatingCountry.objects.get(country = "uk").delivery_address
    # uk_shipping_address =  address_string %(" Suite No %s, " %profile.suite_no)
    #
    # address_string = OperatingCountry.objects.get(country = "us").delivery_address
    # us_shipping_address =  address_string %("%s" %profile.suite_no)
    #
    # #delivery_addresses = [uk_shipping_address]
    #
    # delivery_addresses = [us_shipping_address, uk_shipping_address]

    mm.storefront_name == "volkmannexpress"
    return render(request, 'volkmann/profile_view.html', {'profile': profile, 'decrypt_bvn_no': bvn_no,
                                                              'count_items': count_items})  # 'delivery_addresses': delivery_addresses},

    # else:
    #   return redirect(reverse("general:address_activation", args = [username]))


@login_required(login_url='/volk/login/')
def edit_profile_volk(request, username=None):
    # try:
    #    user = User.objects.get(username = username)
    # except User.DoesNotExist:
    #    raise Http404
    try:
        shipping_item = ShippingItem.objects.filter(user=request.user)
        count_items = shipping_item.filter(ordered=False).count()
    except:
        count_items = 0

    mm = marketing_member(request)

    if request.user.is_authenticated():

        if username == "None":
            mm.storefront_name == "volkmannexpress"
            return redirect("/volk/login/?next=" + reverse("general:edit_profile_volk", args=[None]))
        username = request.user
        # user = get_object_or_404(User, username = username)
        user = get_marketing_member_user(request, username)

        if request.method == "POST":
            form = EditProfileForm()
            form = EditProfileForm(request.POST, request.FILES, instance=user.useraccount)
            if form.is_valid():
                # address_book = AddressBook.objects.filter(user = request.user)
                # for a in address_book:
                #    b = AddressBook(title = form.cleaned_data['title'],telephone   = form.cleaned_data['telephone'],\
                #                               address = form.cleaned_data['address'],city = form.cleaned_data['city'], postal_code = form.cleaned_data['postal_code'], state = form.cleaned_data['state'],\
                #                               country     = form.cleaned_data['country'])
                #    b.save()
                form.save()

                # update first and last name of the user
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                # if form.cleaned_data['country']:
                #    address = AddressBook.objects.filter(user = request.user)[:0]
                return redirect(reverse("general:profile", args=[username]))
            # print form.errors
        else:
            form = EditProfileForm(instance=user.useraccount)
        mm.storefront_name == "volkmannexpress"
        return render(request, 'volkmann/profile.html',
                          {'form': form, 'user_details': user, 'count_items': count_items})
            # return render(request, 'user_profile/edit_profile.html', {'form': form, 'user_details': user},
    else:
        mm.storefront_name == "volkmannexpress"
        return redirect("/volk/login/?next=" + reverse("general:edit_profile_volk", args=[None]))
