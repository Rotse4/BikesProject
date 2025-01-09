from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse

from cart.serializers import OrderItemSerializer, OrderSerializer
from cart.daraja import MpesaClient
from cart.models import Order, OrderItem, Payment
from item.models import Item


# Create your views here.


@extend_schema(
    operation_id="submit_order",
    summary="Submit a new order",
    description="Submit an order with items and payment details.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "quantity": {"type": "integer", "example": 2},
                        },
                        "required": ["id", "quantity"],
                    },
                },
                "payment_number": {"type": "string", "example": "0712345678"},
            },
            "required": ["items", "payment_number"],
        }
    },
    responses={
        200: OpenApiResponse(description="Order submitted successfully."),
        422: OpenApiResponse(
            description="Validation errors.",
            examples={
                "application/json": {"message": ["At least one item should be given."]}
            },
        ),
    },
)
@api_view(
    [
        "POST",
    ]
)
def submit_order(request):
    if request.method == "POST":
        post_data = request.POST
        # print(request.user_id)
        # user = Account.objects.get(id=77)
        user = request.account
        account = user.id
        print("my " + str(user.username))
        # print(user.is_active)
        data_with_account = request.data.copy()
        # print(data_with_account)
        data_with_account["account"] = account
        serializer = OrderSerializer(data=data_with_account)
        if serializer.is_valid():
            order = serializer.save()
            order.start_time = timezone.now()
            order.save()
            print(order.account)
            cart_items = request.data.get("items", [])

            if len(cart_items) < 1:
                return Response(
                    status=422, data={"message": "Atleast one item should be given "}
                )

            cumulativePrice = 0
            for cart_item in cart_items:
                item = Item.objects.get(id=cart_item["id"])
                orderItem = OrderItem()
                orderItem.item = item
                orderItem.order = order
                orderItem.price = item.price
                orderItem.quantity = cart_item["quantity"]
                cumulativePrice = cumulativePrice + orderItem.total()
                orderItem.save()
            order.total = cumulativePrice
            order.save()
            payer_phone = request.data.get("payment_number")
            # access_token = "pbtAXlE4XTbAUx5N2e1ht0eR62MH"
            mpesa_callback = "http://app.sasakonnect.net:23022/cart/callback"
            mpesa_client = MpesaClient()
            response = mpesa_client.make_stk_push(
                order.total, payer_phone, mpesa_callback, "174379", "Pay for goods"
            )
            print(response["CheckoutRequestID"])

            payment = Payment.objects.create(
                phone_no=payer_phone, mpesa_transaction_id=response["CheckoutRequestID"]
            )

            order.payment = payment
            order.save()

            return Response(serializer.data)

        else:
            print("not valid")
            return Response(serializer.errors)


@extend_schema(
    operation_id="create_order_item",
    summary="Create order items",
    description="Create order items based on the provided data.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "item": {"type": "integer", "example": 1},
                "quantity": {"type": "integer", "example": 2},
            },
            "required": ["item", "quantity"],
        }
    },
    responses={
        200: OpenApiResponse(
            description="Order item created successfully."
        ),
        400: OpenApiResponse(
            description="Validation errors.",
            examples={
                "application/json": {
                    "item": ["This field is required."],
                }
            },
        ),
    },
)
@api_view(["POST"])
def order_items(request):
    food_id = request.data.get("item")
    # print(food_id)
    seralizer = OrderItemSerializer(data=request.data)
    # print(seralizer)
    if seralizer.is_valid():
        orderItem = seralizer.save()
        print(orderItem.item)
    else:
        print("wacha ufala buana")

    return Response(seralizer.data)


@extend_schema(
    operation_id="make_stk_push",
    summary="Initiate STK push payment",
    description="Initiate an STK push payment.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "example": 100.0},
                "phone_number": {"type": "string", "example": "0712345678"},
                "callback_url": {"type": "string", "example": "http://example.com/callback"},
                "account_reference": {"type": "string", "example": "Order123"},
                "transaction_desc": {"type": "string", "example": "Payment for goods"},
            },
            "required": ["amount", "phone_number", "callback_url"],
        }
    },
    responses={
        200: OpenApiResponse(
            description="STK push initiated successfully."
        ),
        400: OpenApiResponse(
            description="Validation errors.",
            examples={
                "application/json": {
                    "amount": ["This field is required."],
                }
            },
        ),
    },
)
@api_view(["POST", "GET"])
def make_stk_push(request):
    # Get the necessary data from the request
    amount = request.data.get("amount")
    phone_number = request.data.get("phone_number")
    callback_url = request.data.get("callback_url")
    account_reference = request.data.get("account_reference")
    transaction_desc = request.data.get("transaction_desc")

    # Create an instance of the MpesaClient class with the access token
    access_token = "F5ffBeCl03a4ikmV2s37aZbohwCG"
    mpesa_client = MpesaClient(access_token)

    # Make the STK push payment
    response = mpesa_client.make_stk_push(
        amount, phone_number, callback_url, "174379", "Pay for goods"
    )

    # Return the response as the API response
    return Response(response)


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "stkCallback": {
                    "type": "object",
                    "properties": {
                        "ResultCode": {"type": "integer"},
                        "CheckoutRequestID": {"type": "string"},
                    },
                    "required": ["ResultCode", "CheckoutRequestID"],
                }
            },
            "required": ["stkCallback"],
        }
    },
    responses={
        200: {
            "description": "Callback processed successfully",
        }
    },
    description="Handles MPESA payment callbacks and updates the order status.",
)
@api_view(["POST"])
def mpesa_callback(request):
    print(request.data)
    json_response = request.data.get("Body", {}).get("stkCallback", {})
    result_code = json_response.get("ResultCode")
    if result_code == 0:
        mpesa_transaction_id = json_response.get("CheckoutRequestID")
        print(mpesa_transaction_id)
        try:
            data = Payment.objects.get(mpesa_transaction_id=mpesa_transaction_id)
            order = Order.objects.get(payment=data.id)
            order.confirmed = True
            order.save()
            print(order)
        except (Payment.DoesNotExist, Order.DoesNotExist):
            return Response({"error": "Transaction or order not found"}, status=404)

    return Response(status=200)


@extend_schema(
    operation_id="delivered_orders",
    summary="Retrieve delivered orders",
    description="Retrieve all delivered orders.",
    responses={
        200: OpenApiResponse(
            description="List of delivered orders."
        ),
    },
)
@api_view(["GET"])
def delivered(request):
    order = Order.objects.all()
    queryset = OrderItem.objects.all()
    q1 = OrderItem.objects.filter(order=65)
    serializer = OrderItemSerializer(q1, many=True)
    confirmed = Order.objects.filter(confirmed=True)
    serializer1 = OrderSerializer(confirmed, many=True)
    return Response({"orders": serializer1.data})


@extend_schema(
    operation_id="rate_order_item",
    summary="Rate an order item",
    description="Rate an order item after purchase.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "rating_item": {"type": "integer", "example": 1},
                "rating": {"type": "integer", "example": 5},
            },
            "required": ["rating_item", "rating"],
        }
    },
    responses={
        200: OpenApiResponse(
            description="Rating submitted successfully."
        ),
        400: OpenApiResponse(
            description="Validation errors.",
            examples={
                "application/json": {
                    "rating": ["Rate in scale of 1 to 5."],
                }
            },
        ),
    },
)
@api_view(["POST"])
def rate(request):
    rating_item = request.data.get("rating_item")
    print(rating_item)
    rate_item = OrderItem.objects.get(food=rating_item)
    if rate_item.order.confirmed:
        rate_item.rating = request.data.get("rating")
        if int(rate_item.rating) <= 5:
            rate_item.save()
            return Response(
                {
                    "data": rate_item.rating,
                    "rated": "you rated "
                    + str(rate_item)
                    + " "
                    + str(rate_item.rating)
                    + " stars",
                }
            )
        return Response({"rated": "rate in scale of 1 to 5"})
    elif not rate_item.order.confirmed:
        rate_item.rating = None
        rate_item.save()

        return Response({"data": "You can only rate after you buy"})


@extend_schema(
    operation_id="user_orders",
    summary="Retrieve user orders",
    description="Retrieve orders for the authenticated user.",
    responses={
        200: OpenApiResponse(
            description="List of user orders."
        ),
    },
)
@api_view(["GET"])
def userOrder(request):
    user = request.account
    userOrders = Order.objects.filter(account=user)
    orders = []
    o = 0
    for i in userOrders:
        # print("i am " +str(i))
        order_id = userOrders[o]
        serializer = OrderSerializer(order_id)
        # print(serializer.data)
        orders.append(serializer.data)

        o += 1
    return Response({"orders": orders})


@extend_schema(
    operation_id="end_lease",
    summary="End lease for an order",
    description="End the lease for a specific order.",
    responses={
        200: OpenApiResponse(
            description="Lease ended successfully."
        ),
        404: OpenApiResponse(
            description="Order not found.",
        ),
    },
)
@api_view(["POST"])
def end_lease(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.end_time = timezone.now()  # Set the end time to the current time
        order.save()
        return Response(
            {"message": "Lease ended successfully", "end_time": str(order.end_time)}
        )
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)


@extend_schema(
    operation_id="time_spent",
    summary="Calculate time spent on an order",
    description="Calculate the time spent on a specific order.",
    responses={
        200: OpenApiResponse(
            description="Time spent calculated successfully."
        ),
        404: OpenApiResponse(
            description="Order not found.",
        ),
    },
)
@api_view(["GET"])
def time_spent(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        time_spent = timezone.now() - order.start_time
        return Response({"time_spent": str(time_spent)})
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
