from django.shortcuts import render
from django.http import HttpResponse
from .models import Blogpost

# Create your views here.
def index(request):
    allBlog = []
    blogtitle = []
    # fetching blogs category and id from the database
    blogCat = Blogpost.objects.values('category', 'post_id', 'title')
    # adding blogs category in a list
    allCat = {item['category'] for item in blogCat}

    for cat in allCat:
        # Filtering blogs with category wise
        blogcat = Blogpost.objects.filter(category=cat)
        allBlog.append(blogcat)

    blt= Blogpost.objects.all()
    blogtitle.append(blt)
    param = {'allBlog': allBlog, 'blogtitle':blogtitle,}


    return render(request, 'blog/index.html', param)

def blogpost(request, blogid):
    blogpost = Blogpost.objects.filter(post_id=blogid)
    return render(request, 'blog/blogpost.html', {'blogpost':blogpost[0]})