from event.models import Message
from accounts.models import UserProfile

def base_template_vals(request):
    template_var = {}
    template_var["msg_received_list"] = ""
    template_var["msg_unread"] = ""    
    
    if request.user.is_authenticated():
        print "####" + str(request.user)
        current_django_user = UserProfile.objects.filter(
                                    django_user=request.user)[0];
        messages = Message.objects.filter(msg_to=current_django_user)
        template_var["msg_received_list"] = messages
        msg_unread = 0
        for message in messages:
            if message.is_read == False:
                msg_unread += 1
        template_var["msg_unread"] = msg_unread

    return template_var
