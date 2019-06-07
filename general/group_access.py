from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from general.models import UserAccount
from general.custom_functions import marketing_member
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render



@csrf_exempt
def admin_access(request,user_obj):
	# groups = Group.objects.all()
	# groups.delete()
	# useraccount = UserAccount.objects.filter(user__is_staff = True, marketer = mm)
	# return render(request, 'sokohaliAdmin_snippet/access_table.html', {'useraccount': useraccount})

	#print "rP: ",request.POST
	user_action = request.POST.get('user_action')
	user_action_stripped = str(request.POST.get('user_action')).replace('_',' ')
	content_type = ContentType.objects.get_for_model(User)
	mm = marketing_member(request)
	useraccount = UserAccount.objects.filter(user__is_staff = True, marketer = mm)
	permission, created  = Permission.objects.get_or_create(codename=user_action,
                                       name=user_action_stripped,
                                       content_type=content_type)

	user_obj = User.objects.get(id=user_obj)

	if request.POST.get('action') == 'add':
		group, created = Group.objects.get_or_create(name=user_action_stripped)
		group.permissions.add(permission)
		user_obj.groups.add(group)
	else:
		group = Group.objects.get(name=user_action_stripped)
		user_obj.groups.remove(group)

	#print "my groups: ", user_obj.groups.all()
	return render(request, 'sokohaliadmin_snippet/access_table.html', {'useraccount': useraccount})































