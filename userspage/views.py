#ram vai => Neepal@12

from multiprocessing import context
from django.shortcuts import render,redirect,get_object_or_404 # pyright: ignore[reportMissingModuleSource]
from demo_app.models import *
from django.contrib.auth.decorators import login_required # pyright: ignore[reportMissingModuleSource]
from accounts.auth import user_only
from .models import *
from django.db.models import Q # pyright: ignore[reportMissingModuleSource]
from django.contrib import messages # pyright: ignore[reportMissingModuleSource]
from .forms import OrderForm
from .filters import FoodFilter
from . filters import HotelFilter
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator # pyright: ignore[reportMissingModuleSource]


# Create your views here.
def homepage(request):
	foods=Food.objects.all().order_by('-id')
	hotel_filter=HotelFilter(request.GET,queryset=foods)  #filter
	hotel_final=hotel_filter.qs 
	context={
		'foods':hotel_final,
		'hotel_filter':hotel_filter

	}
	return render(request,'client/homepage.html',context)


def foods(request, category_id=None):
    categories = None
    products = None

    if category_id != None:
        categories = get_object_or_404(Category, slug=category_id)
        products = Food.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Food.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'client/foods.html', context)

def food_details(request,food_id):
	food=Food.objects.get(id=food_id)
	category = Category.objects.get(id=food.category.id)

	# recommended_food=Food.objects.filter(category__id=category.id)
	recommended_food = get_recommended_food(category.id)
	context={
		'food':food,
		'recommended_foods':recommended_food,
	}
	return render(request,'client/fooddetails.html',context)



@login_required
@user_only
def add_to_cart(request,food_id):
	user=request.user
	food=Food.objects.get(id=food_id)

	check_item_presence=Cart.objects.filter(user=user,food=food)
	if check_item_presence:
		messages.add_message(request,messages.ERROR,'Recipy already present in the cart')
		return redirect('/mycart')
	else:
		cart=Cart.objects.create(food=food,user=user)
		if cart:
			messages.add_message(request,messages.SUCCESS,'Items added to cart')
			return redirect('/mycart')
		else:
			messages.add_message(request,messages.ERROR,'Unable to add to cart')
			return redirect('/foods')


@login_required
@user_only
def show_cart_items(request):
	user=request.user
	items=Cart.objects.filter(user=user)
	context={
		'items':items
	}
	return render(request,'client/cart.html',context)
	
@login_required
@user_only
def order_form(request,food_id,cart_id):
	user=request.user
	food=Food.objects.get(id=food_id)
	cart_item=Cart.objects.get(id=cart_id)

	if request.method == 'POST':
		form=OrderForm(request.POST)
		if form.is_valid():
			quantity=request.POST.get('quantity')
			if int(quantity)<0:
				messages.add_message(request,messages.ERROR,'Quantity can not be negative')
				return render(request,'client/orderform.html',{'form':form})
			price=food.food_price
			total_price=int(quantity)*int(price)
			contact_no=request.POST.get('contact_no')
			if not (contact_no.isdigit() and len(contact_no) == 10 and contact_no[0] == '9'):
				messages.add_message(request, messages.ERROR, 'Invalid phone number format')
				return render(request, 'client/orderform.html', {'form': form})
			address=request.POST.get('address')
			payment_method=request.POST.get('payment_method')
			payment_status=request.POST.get('payment_status')
			status=request.POST.get('status','Pending')

			order=Order.objects.create(
				food=food,
				user=user,
				quantity=quantity,
				total_price=total_price,
				contact_no=contact_no,
				address=address,
				payment_method=payment_method,
				payment_status=payment_status,
				status=status
			)
			if order.payment_method == 'Cash on Delivery':
				cart=Cart.objects.get(id=cart_id)
				cart.delete()
				messages.add_message(request,messages.SUCCESS,'order successfully')
				return redirect('/myorder')
			elif order.payment_method == 'Esewa':
				context={
					'order':order,
					'cart':cart_item
				}
				return render(request,'client/esewa_payment.html',context)
			else:
				messages.add_message(request,messages.ERROR,'Something went wrong')
				return render(request,'client/orderform.html',{'form':form})

	context={
			'form':OrderForm
	}
	return render(request,'client/orderform.html',context)

@login_required
@user_only
def show_order_items(request):
	user=request.user
	items=Order.objects.filter(user=user)
	context={
		'items':items
	}
	return render(request,'client/order.html',context)


def faqs(request):
	return render(request,'client/faqs.html')

def remove_cart_items(request,cart_id):
	item=Cart.objects.get(id=cart_id)
	item.delete()
	messages.add_message(request,messages.SUCCESS,'item removed from the cart')
	return redirect('/mycart')


    
def showuser(request,order_id):
	form=Order.objects.get(id=order_id)
	
	context={
		'i':form,
	}
	return render(request,'client/showuser.html',context)


def profile_info(request):
	return render(request,'client/profile_info.html')
	
def customer(request):
	if request.user.is_authenticated:
		return render(request,'client/customer.html')
	else:
		return redirect('/')
	
def aboutus(request):
	return render(request,'client/aboutus.html')

def blog(request):
	
	return render(request,'client/blog.html')



def get_recommended_food(category_id):
    # Step 1: Retrieve all movies that have specified genre
    food_list= list(Food.objects.filter(category__id=category_id))

    # Step 2: Sort movies by release date in descending order using Bubble Sort
    for i in range(len(food_list)):
        for j in range(0, len(food_list) - i - 1):
            if food_list[j].food_name > food_list[j + 1].food_name:
                # Swap if the release date of the current movie is greater than the next
                food_list[j], food_list[j + 1] = food_list[j + 1], food_list[j]

    return food_list



def search(request):
    products = []
    product_count = 0
    message = ""

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Food.objects.order_by('food_name').filter(
                Q(food_name__icontains=keyword)
            )
            product_count = products.count()

            if product_count == 0:
                message = f"No food items found for '{keyword}'. Please try another search."

    context = {
        'products': products,
        'product_count': product_count,
        'message': message,
    }
    return render(request, 'client/foods.html', context)

from .recommendation import get_recommended_food_by_order_history  # Import the recommendation function

def recommended(request):
    user = request.user  # Get the logged-in user

    # Step 1: Retrieve the user's order history
    items = Order.objects.filter(user=user)
    
    # Step 2: Get recommended food based on order history (from the same categories as previously ordered items)
    recommended_foods = get_recommended_food_by_order_history(user.id)
    
    # Step 3: Prepare context to pass to the template
    context = {
        'items': items,  # Include all past orders for the user
        'recommended_foods': recommended_foods,  # Include recommended food based on categories
    }

    return render(request, 'client/recommended.html', context)