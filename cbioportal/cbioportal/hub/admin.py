import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf.urls import url
from django.contrib import admin

from cbioportal.hub.models import *

logger = logging.getLogger(__name__)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'uid')
    #fieldsets = ( (None, { 'fields': (( 'first_name', 'last_name'), ('username', 'email'), 'bio', 'user_permissions') }),    )
    fieldsets = ( (None, { 'fields': (( 'first_name', 'last_name'), ('username', 'email'), 'bio' ) }),    )
    actions = [ 'send_email', 'reset_token', 'reset_password', 'remove_users' ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context = None):
        extra_context = extra_context or {}
        extra_context['messages'] = messages.get_messages(request)
        return super(UserAdmin, self).changelist_view(request, extra_context)

    def reset_password(self, request, queryset):
        msg = ""
        for user in queryset:
            user.generatenewpassword()
            msg += "%s, " % user.username
            logger.debug("reset_password: %s" % user)
        messages.success(request, "Password reset for: %s" % msg)
    reset_password.short_description = 'Reset password'


    def send_email(self, request, queryset):
        return render(
            request,
            'admin/sendemail.html',
            context = { 'users': queryset, }
        )
    send_email.short_description = 'Send email in a mass'

    def remove_users(self, request, queryset):
        msg = ""
        oops = ""
        for user in queryset:
            try:
                user.remove()
                super().delete_model(request, user)
                msg += "%s, " % user
                logger.info("removed user: %s" % user)
            except Exception as e:
                logger.error("remove_user: %s -- %s" % (user, e))
                oops += "%s (%s), " % (user, e)
        if len(msg):
            messages.success(request, "Deleted: %s" % msg)
        if len(oops):
            messages.warning(request, "Ooopsed: %s" % oops)
    remove_users.short_description = 'Delete users in a neat way'

    def save_model(self, request, user, form, changed):
        from cbioportal.lib.sendemail import send_new_password
        try:
            user_old = User.objects.get(username = user.username)
            if user_old.email != user.email:
                # user.changeemail()  #TODO: if e-mail may change then gitlab user details have to be updated accordingly
                raise NotImplementedError
        except User.DoesNotExist:
            user.create()
            logger.info("user created: %s" % user)
            send_new_password(user)
        super().save_model(request, user, form, changed)

    def delete_model(self, request, user):
        user.remove()
        logger.info("removed user: %s" % user)
        super().delete_model(request, user)


def send_email(request):
    from cbioportal.lib import sendemail
#FIXME: authorize
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()
    if not len(subject):
        messages.error(request, "Mails are not sent out. Provide a subject")
        return redirect('/admin')
    if not len(message):
        messages.error(request, "Mails are not sent out. Provide a message")
        return redirect('/admin')
    subject = "[ cbioportal ] %s" % subject
    okay = []
    notokay = []
    for uid in request.POST.getlist('userlist'):
        try:
            user = User.objects.get(id = uid)
            status = sendemail(user.email, subject, message)
            if status == 0:
                logger.info("mail with subject %s sent to %s" % (subject, user.email))
                okay.append(user.username)
            else:
                logger.debug("cannot sent mail with subject %s to %s" % (subject, user.email))
                notokay.append(user.username)
        except User.DoesNotExist:
            logger.error("Mass email: Someone hacking? uid = %d not found" % uid)
            messages.error(request, "Loop broken, uid not found!")
            break
    if len(okay):
        messages.success(request, "mail sent to: " + ",".join(okay))
    if len(notokay):
        messages.error(request, "mail not sent to: " + ",".join(notokay))
    return redirect('/admin')

urlpatterns = [
    url(r'^sendemail', send_email, name = 'send-email'),
]

