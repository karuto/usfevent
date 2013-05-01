from accounts.models import UserProfile
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from event.models import Comment, Event, Message, Like
from notification.views import sys_notification
from taggit.managers import TaggableManager
from taggit.models import Tag
import time


def index(request):
    """
    """
    template_var = {}
    up = UserProfile.objects.filter(django_user=request.user)
    template_var["likes"] = Like.objects.filter(user=up[0])
    
    try:
        event_list = Event.objects.all().order_by('id')
    except Event.DoesNotExist:
        raise Http404
    output = ', '.join([e.title for e in event_list])    
    template_var["events"] = output	
    return render_to_response("event/index.html", template_var,
                              context_instance=RequestContext(request))


def single(request, pk):
    """
    """
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
    template_var["auth_users"] = User.objects.all()
    current_django_user = UserProfile.objects.filter(django_user=request.user)[0]
        
    return render_to_response("event/event_single.html", template_var,
                              context_instance=RequestContext(request))
    

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

	
def add_comment(request, pk, pk2):
    #pk is event.id
    #pk2 is user.id
    print pk;
    template_var = {}
    p = request.POST
    
    if p.has_key("content") and p["content"]:
        if request.user.is_authenticated():
            comment = Comment(event=Event.objects.get(id=pk))
            comment.user = UserProfile.objects.get(django_user=request.user)
            comment.content = p["content"]
            comment.save()
            
            #sys notification
            from_user = UserProfile.objects.get(django_user=pk2) #who's event that is commented on
            to_user = Event.objects.get(id=pk).author
            event_id = pk
            sys_notification(to_user, "add_comment", from_user, event_id)
    
    return single(request, pk)
    

	
def like_event(request, pk):
    print pk;
    template_var = {}
    if request.user.is_authenticated():
        like = Like(event=Event.objects.get(id=pk))
        like.user = UserProfile.objects.filter(django_user=request.user)[0]
        like.save()
    return redirect('index')


def share_email(request, pk):
    print pk;
    template_var = {}
    
    subject, from_email, to = 'Your friend shared an event with you on Dons Affairs!', 'from@example.com', 'donsaffair@gmail.com'
    to = request.POST["email_to"] #default is sending to self 'donsaffair@gmail.com'
    link = request.POST["abs_url"]
    text_content = 'This is an important message. Your friend shared an event link with you. ' + link
    html_content = '<p>Hi Dear,</p><p>Your friend shared an exciting event with you on <a href="http://mtk.im/usf">Don\'s Affairs</a>!</p>' + '<p><a href="'+ link+ '">Here goes the link to the event.</a><br>Feel free to check it out!</p><p><br>With love,<br>Don\'s Affair Team</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    return redirect('index')
    

def save_event(request):
    template_var = {}
    template_var["allusers"] = UserProfile.objects.all()

    current_django_user = UserProfile.objects.filter(django_user=request.user)[0]
    
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
    if request.user.is_authenticated():
        from_user = UserProfile.objects.get(django_user=request.user)
        if request.method=="POST":
            title_ = request.POST["title"]
            body_ =  request.POST["body"]
            refer_ = request.POST["refer"]
            date_ = request.POST["date"]
            try:
                time.strptime(date_, '%m/%d/%Y')
            except ValueError:
                current_day = datetime.now().strftime("%Y-%m-%d %H:%M")
                date_ = datetime.strptime(current_day, '%Y-%m-%d %H:%M')
                print date_
                
            loc_ = request.POST["loc"]
            tags_ = request.POST["tags"]
            if(len(tags_) == 0):
                tags_ = "untagged"
            try:
                image1_ = request.FILES["picture"]
                event = Event(title = title_, body= body_, location = loc_, refer = refer_, event_time = date_, image1 = image1_, author = from_user)
            except:
                event = Event(title = title_, body= body_, location = loc_, refer = refer_, event_time = date_, author = from_user)
        
            #event = Event(title = title_, body= body_, location = loc_, refer = refer_, event_time = date_, image1 = image1_)
            event.save()
            tags = splitTags(tags_)
            for tag in tags:
                event.tags.add(tag)
            event.save()
            return HttpResponseRedirect(reverse("index"))    

    return render_to_response("event/event_post.html",template_var,context_instance=RequestContext(request))


def splitTags(user_input):
        elements = []
        if ',' in user_input:
                elements = user_input.split(',');
        elif ' ' in user_input:
                elements = user_input.split(' ');
        else:
                elements.append(user_input)

        tags = []
        for element in elements:
                element = element.strip(' \t\n\r').lower()
                if(len(element) == 0): continue
                if element not in tags:
                    tags.append(element)
        
        for tag in tags:
                print "(" + tag+ ")"
        return tags


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
        event_id_list = []
        events_found = []
        events_found_advanced = []
        events_found_basic = []
        checkbox_session = []
        #sorted_method_session = []
        advanced_search = False
        tags = Tag.objects.all()
        template_var["tags"] = tags

        query_tags = request.GET.getlist('query_tag')
        if len(query_tags) > 0:  # at least one checkbox selected
            advanced_search = True
            query_tag_list = []
        
            #strip >>u''<< prefix
            for query_tag in query_tags:
                checkbox_session.append(str(query_tag))
                query_tag_list.append(str(query_tag))
                
            events_found_advanced = Event.objects.filter(tags__name__in=query_tag_list)
               
        query = request.GET.get('query', '').strip('\t\n\r')
        if query == '' : #first came in/accidentily type space/..
            if advanced_search:
                events_found_advanced = events_found_advanced
            else:
                events_found_basic = Event.objects.all().order_by("-created")
                
        else:
            if advanced_search:
                events_found_advanced = events_found_advanced.filter(tags__name__in=[query])
            else:
                events_found_basic = Event.objects.filter(tags__name__in=[query])

        #finally
        if advanced_search:
            #take out duplicated result
            for event_found_advanced in events_found_advanced:
                if(event_found_advanced.id not in event_id_list):
                    event_id_list.append(event_found_advanced.id)
                    events_found.append(event_found_advanced)
        else:
            for event in events_found_basic:
                events_found.append(event)

        #sort result
        sorted_method = request.GET.get('sorted_method', 'desc') #default is desc
        if sorted_method == 'desc':
            events_found.sort(key=lambda event: event.event_time, reverse=True)  
        elif sorted_method == 'asc':
            events_found.sort(key=lambda event: event.event_time, reverse=False)  
        elif sorted_method == 'alphabet':
            events_found.sort(key=lambda event: event.title.lower(), reverse=False)  
           
        template_var["events_found"] = events_found

        request.session["sorted_method_session"] = sorted_method
        request.session["checkbox_session"] = checkbox_session
        request.session["query_session"] = query
        return render_to_response("event/event_search_results.html",template_var,context_instance=RequestContext(request))

    return render_to_response("event/event_search_results.html",template_var,context_instance=RequestContext(request))
    
    
