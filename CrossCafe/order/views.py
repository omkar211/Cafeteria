"""Manage Order
"""
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.http import Http404, JsonResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core import serializers
import json
from order.models import Order
from menu.models import FoodItem
from . import OrderDao, ViewUtil

EXTRA_CHARGES = 30;
DELIVERY_CHARGES = 20;

def createOrder(request):
	if request.method == 'POST':
		cart = eval(request.POST['cart'])
		restaurant_id = request.POST['restaurant_id']
		cart_items = []
		total = 0
		for items in cart:
			item_object = FoodItem.objects.get(item_id=items['id'])
			cart_items.append({'item_name': item_object.name, 'item_price': item_object.price})
			total += item_object.price
		grand_total = total + EXTRA_CHARGES + DELIVERY_CHARGES
		new_order = Order(order_items=str(cart_items), status='draft', amount=total, extra_charges=EXTRA_CHARGES, delivery_charges=DELIVERY_CHARGES, restaurant_id=restaurant_id, order_type='online')
		new_order.save()
		print new_order.order_id
		review_page_url = '/order/review'
		return HttpResponseRedirect(review_page_url)
	else:
		return HttpResponseNotFound('<h1>404 Page not found</h1>')

def reviewOrder(request):
	cart = Order.objects.filter(status='draft')
	if(cart):
		return render(request, 'order/review_order.html', {'cart': cart})
	else:
		return render(request, 'order/review_order.html')

@csrf_exempt
def placeorder(request):
    customer_id = ViewUtil.ViewUtil.get_customer_id(request)
    order = ViewUtil.ViewUtil.prepare_order(request, customer_id)
    return HttpResponse(serializers.serialize('json', [order, ]))

#Update the payment details in the order table
#Trigger a notification to Attendar for Accept/Reject the order
#Navigate to a page showing Confirmation to customer saying payment successfuly done/pay at your door in case of COD, order is on hold for acceptance
@csrf_exempt
def pay(request):
    order_id = request.POST.get('order_id')
    order_dao = OrderDao.OrderDao.getInstance()
    order = order_dao.find_by_id(order_id)
    order = ViewUtil.ViewUtil.get_items_from_payment_page(request, order)
    order = order_dao.update(order)
    return JsonResponse(ViewUtil.ViewUtil.get_payment_json_response(order))

def orderdetails(request):
    #order_id = str(1)
    #orderDao = OrderDao.get_instance()
    #order = orderDao.findById(order_id)
    return render(request, 'order/orderdetails.html', {})

@csrf_exempt
def get_customer_order(request):
    if not request.method == 'POST':
        raise Http404("Invalid Request")
    customer_id = request.POST.get('customer_id')
    order = OrderDao.OrderDao.getInstance().find_by_customer_id(customer_id)
    if order is None:
        order = '{}'
    return HttpResponse(serializers.serialize('json', order))

@csrf_exempt
def get_restaurant_order(request):
    if not request.method=='POST':
        raise Http404("Invalid Request")
    restaurant_id = request.POST.get('restaurant_id')
    order = OrderDao.OrderDao.getInstance().find_by_restaurant_id(restaurant_id)
    if order is None:
        order = '{}'
    #result = [{'order': o.area} for r in allAreas]
    orders = serializers.serialize('json', list(order))
    return HttpResponse(orders)