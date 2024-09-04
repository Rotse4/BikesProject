from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from cart.admin import OrderItemSerializer, OrderSerializer
from cart.daraja import MpesaClient
from cart.models import Order, OrderItem, Payment
from item.models import Item

# Create your views here.

@api_view(['POST',])
def submit_order(request):
    if request.method == 'POST':
        post_data = request.POST
        # print(request.user_id)
       # user = Account.objects.get(id=77)
        user=request.account
        account=user.id
        print('my ' + str(user.username))
        # print(user.is_active)
        data_with_account = request.data.copy()
        # print(data_with_account)
        data_with_account['account'] = account
        serializer = OrderSerializer(data=data_with_account)
        if serializer.is_valid():
            order=serializer.save()
            print(order.account)
            cart_items = request.data.get('items', [])
              
            if len(cart_items)<1 :
              return Response(status=422,data={"message":"Atleast one item should be given "})

                 
            
            cumulativePrice=0
            for item in cart_items:
                item=Item.objects.get(id=item['id']) 
                orderItem=OrderItem()
                orderItem.item=item
                orderItem.order=order
                orderItem.price=item.price
                orderItem.quantity=item['quantity']
                cumulativePrice=cumulativePrice+orderItem.total()
                orderItem.save()
            order.total=cumulativePrice
            order.save()
            payer_phone=request.data.get("payment_number");
            # access_token = "pbtAXlE4XTbAUx5N2e1ht0eR62MH"
            mpesa_callback="http://app.sasakonnect.net:23022/cart/callback"
            mpesa_client = MpesaClient()
            response = mpesa_client.make_stk_push(order.total, payer_phone, mpesa_callback, '174379', 'Pay for goods')
            print(response["CheckoutRequestID"])

            payment = Payment.objects.create(phone_no=payer_phone, mpesa_transaction_id=response["CheckoutRequestID"])

            order.payment=payment;
            order.save()

            return Response(serializer.data)

        else:
            print("not valid")
            return Response(serializer.errors)


        

@api_view(['POST'])
def order_items(request):
        food_id = request.data.get('item')
        # print(food_id)
        seralizer = OrderItemSerializer(data=request.data)
        # print(seralizer)
        if seralizer.is_valid():
            orderItem = seralizer.save()
            print(orderItem.food)
        else:
            print("wacha ufala buana")

        
        return Response(seralizer.data)


@api_view(['POST', 'GET'])
def make_stk_push(request):
    # Get the necessary data from the request
    amount = request.data.get('amount')
    phone_number = request.data.get('phone_number')
    callback_url = request.data.get('callback_url')
    account_reference = request.data.get('account_reference')
    transaction_desc = request.data.get('transaction_desc')
    
    # Create an instance of the MpesaClient class with the access token
    access_token = "F5ffBeCl03a4ikmV2s37aZbohwCG"
    mpesa_client = MpesaClient(access_token)
    
    # Make the STK push payment
    response = mpesa_client.make_stk_push(amount, phone_number, callback_url, '174379', 'Pay for goods')
    
    # Return the response as the API response
    return Response(response)


@api_view(['POST'])
def mpesa_callback(request):
        print(request.data);
        # json_response = request.data.get("")
        json_response = request.data.get('Body', {}).get('stkCallback', {})
        result_code = json_response.get('ResultCode')
        if(result_code==0):            
            mpesa_transaction_id = json_response.get('CheckoutRequestID')
            print(mpesa_transaction_id)
            data=Payment.objects.get(mpesa_transaction_id=mpesa_transaction_id)
            order=Order.objects.get(payment=data.id)
            order.confirmed=True
            order.save()
            print(order)

        return Response(status=200)


@api_view(['GET'])
def delivered(request):
    order=Order.objects.all()
    queryset = OrderItem.objects.all()  
    q1 = OrderItem.objects.filter(order=65)
    serializer =OrderItemSerializer(q1, many =True)
    confirmed=Order.objects.filter(confirmed=True)
    serializer1 =OrderSerializer(confirmed, many=True)
    return Response({"orders":serializer1.data})


@api_view(['POST'])
def rate(request):
    rating_item=(request.data.get('rating_item'))
    print(rating_item)
    rate_item = OrderItem.objects.get(food=rating_item)
    if rate_item.order.confirmed:
        rate_item.rating=request.data.get('rating')
        if int(rate_item.rating)<=5:
            rate_item.save()
            return Response({"data":rate_item.rating, "rated": "you rated "+str(rate_item)+ " "+str(rate_item.rating)+ " stars"})
        return Response({"rated": "rate in scale of 1 to 5"})
    elif not rate_item.order.confirmed:
        rate_item.rating=None
        rate_item.save()

        return Response({"data":"You can only rate after you buy"})
               


@api_view(['GET'])
def userOrder(request):
    user=request.account
    userOrders = Order.objects.filter(account =user)
    orders =[]
    o=0
    for i in userOrders:
        # print("i am " +str(i))
        order_id =  userOrders[o]
        serializer = OrderSerializer(order_id)
        # print(serializer.data)
        orders.append(serializer.data)
        
        o+=1
    return Response({"orders":orders})