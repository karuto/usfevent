from accounts.models import UserProfile
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from event.models import Comment, Event, Message, Like
from taggit.managers import TaggableManager

def index(request):
    template_var = {}
    
    # Retrieve s
    up = UserProfile.objects.filter(django_user=request.user)
    template_var["likes"] = Like.objects.filter(user=up[0])
    
    try:
        event_list = Event.objects.all().order_by('id')
    except Event.DoesNotExist:
        raise Http404
    output = ', '.join([e.title for e in event_list])    
    template_var["events"] = output	
    return render_to_response("event/index.html", template_var, context_instance=RequestContext(request))


def single(request, pk):
    template_var = {}
    try:
        e = Event.objects.get(pk=int(pk))
        template_var['event'] = e
    except Event.DoesNotExist:
        raise Http404
    try:
        template_var['comments'] = Comment.objects.filter(event=e)
    except Comment.DoesNotExist:
        template_var['comments'] = []
        
    # Save the date related
    
    template_var["allusers"] = UserProfile.objects.all()
    current_django_user = UserProfile.objects.filter(django_user=request.user)[0];
        
    return render_to_response("event/event_single.html", template_var, context_instance=RequestContext(request))
    

def archives(request):
    template_var = {}
    try:
        template_var["events"] = Event.objects.all().order_by("-event_time")
        # print template_var["events"]
    except Event.DoesNotExist:
        raise Http404
    return render_to_response("event/event_listview.html", template_var, context_instance=RequestContext(request))


def tagpage(request, tag):
    template_var = {}
    template_var["tag"] = tag
    try:
        template_var["events"] = Event.objects.filter(tags__name__in = [tag])
        # This does return actual event objects
        # print template_var["events"]
    except Event.DoesNotExist:
        print "Tag event does not exist!"
        raise Http404
    return render_to_response("event/tag_single.html", template_var, context_instance=RequestContext(request))

	
def add_comment(request, pk):
    print pk;
    template_var = {}
    p = request.POST
    
    if p.has_key("content") and p["content"]:
        if request.user.is_authenticated():
            comment = Comment(event=Event.objects.get(id=pk))
            comment.user = UserProfile.objects.filter(django_user=request.user)[0]
            comment.content = p["content"]
            comment.save()
    
    return redirect('index')
    

	
def like_event(request, pk):
    print pk;
    template_var = {}
    if request.user.is_authenticated():
        like = Like(event=Event.objects.get(id=pk))
        like.user = UserProfile.objects.filter(django_user=request.user)[0]
        like.save()
    return redirect('index')
    

def save_event(request):
    template_var = {}
    template_var["allusers"] = UserProfile.objects.all()

    current_django_user = UserProfile.objects.filter(django_user=request.user)[0];
    
    if request.method=="POST":
        if request.user.is_authenticated():
            message = Message()
            message.msg_from = UserProfile.objects.filter(django_user=request.user)[0]
            message.msg_to = UserProfile.objects.filter(id__exact=request.POST["msg_to_django_user_id"])[0]
            message.content = request.POST["content"]
            message.save()

        return HttpResponseRedirect("/events/msg/")
        
    return render_to_response("event/message_send.html",template_var,context_instance=RequestContext(request))
    


def post(request):
    template_var = {}
    if request.method=="POST":
        title_ = request.POST["title"]
        body_ =  request.POST["body"]
        refer_ = request.POST["refer"]
        date_ = request.POST["date"]
        loc_ = request.POST["loc"]
        tags_ = request.POST["tags"]
        image1_ = request.FILES["picture"]

    
        event = Event(title = title_, body= body_, location = loc_, refer = refer_, event_time = date_, image1 = image1_)
        event.save()
        event.tags.add(tags_)
        event.save()
        return HttpResponseRedirect(reverse("index"))    

    return render_to_response("event/event_post.html",template_var,context_instance=RequestContext(request))


def msg_send(request):
    template_var = {}
    template_var["allusers"] = UserProfile.objects.all()

    current_django_user = UserProfile.objects.filter(django_user=request.user)[0];
    template_var["msg_sent_list"] = Message.objects.filter(msg_from=current_django_user)
    template_var["msg_received_list"] = Message.objects.filter(msg_to=current_django_user)
    
    if request.method=="POST":
        if request.user.is_authenticated():
            message = Message()
            message.msg_from = UserProfile.objects.filter(django_user=request.user)[0]
            message.msg_to = UserProfile.objects.filter(id__exact=request.POST["msg_to_django_user_id"])[0]
            message.content = request.POST["content"]
            message.save()

        return HttpResponseRedirect("/events/msg/")
        
    return render_to_response("event/message_send.html",template_var,context_instance=RequestContext(request))
    
    
    
    
def search(request):
    template_var = {}
    if request.method=="GET":

        query = request.GET.get('query', '').strip('\t\n\r')
        if query == '' : #first came in/accidentily type space/..
            local_events_found = Event.objects.all().order_by("-created")
        else:
            local_events_found = Event.objects.filter(tags__name__in=[request.GET.get('query', '')])

        events_found = []
        for event in local_events_found:
            events_found.append(event)

        sorted_method = request.GET.get('sorted_method', 'desc') #default is desc
        if sorted_method == 'desc':
            events_found.sort(key=lambda event: event.event_time, reverse=True)  
        elif sorted_method == 'asc':
            events_found.sort(key=lambda event: event.event_time, reverse=False)  
        elif sorted_method == 'alphabet':
            events_found.sort(key=lambda event: event.title, reverse=False)  
           
        template_var["events_found"] = events_found

        request.session["sorted_method"] = sorted_method

        return render_to_response("event/event_search_results.html",template_var,context_instance=RequestContext(request))

    return render_to_response("event/event_search_results.html",template_var,context_instance=RequestContext(request))
