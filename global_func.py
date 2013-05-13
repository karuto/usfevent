from accounts.models import UserProfile
from notification.models import Message
from taggit.models import Tag


def base_template_vals(request):
    template_var = {}
    template_var["msg_received_list"] = ""
    template_var["msg_unread"] = ""    
    
    if request.user.is_authenticated():
        current_user_profile = UserProfile.objects.filter(
                                    django_user=request.user)[0]
        template_var["u"] = current_user_profile
        messages = Message.objects.filter(msg_to=current_user_profile)
        template_var["msg_received_list"] = messages
        msg_unread = 0
        for message in messages:
            if message.is_read == False:
                msg_unread += 1
        template_var["msg_unread"] = msg_unread

    # Used in numerous cases, basically anywhere with time-related form fields
    time_hours = ["00","01","02","03","04","05","06","07","08","09","10","11",
    "12","13","14","15","16","17","18","19","20","21","22","23"]
    template_var["time_hours"] = time_hours

    return template_var
