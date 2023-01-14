from django.shortcuts import render
from django.http import HttpResponse
from .models import Porduct, Orders, Contact, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from  paytm  import Checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'

# Create your views here.
def index(request):
    # products = Porduct.objects.all()
    # print(products)
    # n = len(products)
    # nSlides = n//4 + ceil((n/4)-(n//4))


    allProds = []
    # Thiis will fetch all the product category from the database
    catProds = Porduct.objects.values('category', 'id')
    # adding all product category in the list
    cats = {item['category'] for item in catProds}
    for cat in cats:
        # filtering prodcut form category wise
        prod = Porduct.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(nSlides), nSlides])
    # params = {'no_of_slides': nSlides, 'range':range(nSlides), 'product': products}
    # allProds = [[products, range(nSlides), nSlides],
    #             [products, range(nSlides), nSlides]]
    params = {'allProds': allProds}
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower()  or query in item.category.lower() :
        return True

    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    # Thiis will fetch all the product category from the database
    catProds = Porduct.objects.values('category', 'id')
    # adding all product category in the list
    cats = {item['category'] for item in catProds}
    for cat in cats:
        # filtering prodcut form category wise
        prodtemp = Porduct.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(nSlides), nSlides])

    params = {'allProds': allProds, 'msg' :""}
    if len(allProds) == 0 or len(query)<2:
        params= {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)



def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    # serializers.serialize('json',OrderUpdate.objects.timestamp())
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({ "status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)

            else:
                 return HttpResponse('{"status": "noitem"}')
        except Exception as e:
            return HttpResponse('{"stats": "error"}')

    return render(request, 'shop/tracker.html')


def prodView(request, myid):
    product = Porduct.objects.filter(id=myid)
    return render(request, 'shop/prodView.html',
                  {'product': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        phone = request.POST.get('phone', '')
        zip_code = request.POST.get('zip_code', '')
        order = Orders(name=name, email=email, phone=phone, address=address,
                        city=city, state=state, zip_code=zip_code, items_json=items_json, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'shop/Checkout.html', {'thank': thank, 'id': id })
        # Request paytm to transfer the amount to your account after payment done by user
        param_dict={


                'MID': 'Enter merchant id',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                 'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request,'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/Checkout.html')



@csrf_exempt
def handlerequest(request):
    # paytm will send request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i]:form[i]
        if i =="CHECKSUMHASH":
            checksum=form[i]
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('Order Successful')
    else:
        print('Order was not successful because'+ response_dict['RESPMSG'])
    return render(request, 'shop/paytmentstatus.html', {'response':response_dict})
    pass
