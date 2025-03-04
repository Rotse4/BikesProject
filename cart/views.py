from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)

from account.permissions import has_perms
from cart.serializers import OrderDurationSerializer, OrderItemSerializer
from cart.daraja import MpesaClient
from cart.models import OrderItem, Payment
from item.models import Item
from decimal import Decimal

from shop.models import OrderDuration, Shop


# Create your views here.


@extend_schema(
    operation_id="order_bike",
    description="Submit a bike order with payment details. Includes M-Pesa STK push.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "bike_id": {
                    "type": "integer",
                    "description": "ID of the bike being ordered.",
                },
                "payment_no": {
                    "type": "string",
                    "description": "Phone number to use for payment.",
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration in hours for which the bike is rented (e.g., 1, 2, 3, 8, 24).",
                },
            },
            "required": ["bike_id", "payment_no", "usage_time"],
        }
    },
    responses={
        200: {
            "description": "Order placed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Order placed successfully.",
                        "order_id": 123,
                        "payment_status": "pending",
                    }
                }
            },
        },
        400: {
            "description": "Invalid request data.",
            "content": {"application/json": {"example": {"error": "Invalid data."}}},
        },
    },
)
@api_view(["POST"])
def orderBike(request):
    user = request.account
    account = user.id
    data_with_account = request.data.copy()
    data_with_account["account"] = account
    data_with_account["item"] = data_with_account.get("bike_id")
    data_with_account["active"] = True

    usage_time = data_with_account.get("usage_time")

    if not usage_time:
        return Response({"error": "Usage time is required."}, status=400)

    try:
        order_duration = OrderDuration.objects.get(
            time=str(usage_time)
        )  # Ensure string match
        price = Decimal(order_duration.price)  # Convert price from string to Decimal
    except OrderDuration.DoesNotExist:
        valid_times = list(OrderDuration.objects.values_list("time", flat=True))
        return Response(
            {
                "error": f"Invalid usage time. Allowed values: {', '.join(map(str, valid_times))}."
            },
            status=400,
        )

    data_with_account["price"] = price

    serializer = OrderItemSerializer(data=data_with_account)
    if serializer.is_valid():
        order = serializer.save()
        order.start_time = timezone.now()
        order.save()

        print(f"Order active is {order.active}")

        return Response(
            {
                "message": "Bike order created successfully.",
                "order_id": order.id,
                "price": str(order.price),
                "start_time": order.start_time,
            },
            status=201,
        )
    else:
        return Response({"error": serializer.errors}, status=400)


@extend_schema(
    operation_id="end_order",
    description="End an active order and calculate the final price. Payment initiation is handled via Mpesa.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "The ID of the order to end.",
                    "example": 12345,
                },
                "payment_no": {
                    "type": "string",
                    "description": "The phone number for Mpesa payment.",
                    "example": "254712345678",
                },
            },
            "required": ["order_id", "payment_no"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Order ended successfully."},
                "order_id": {"type": "integer", "example": 12345},
                "final_price": {"type": "string", "example": "120.50"},
                "payment_status": {"type": "string", "example": "pending"},
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Order ID and payment number are required.",
                },
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "Order not found or already completed.",
                },
            },
        },
        500: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "An unexpected error occurred."},
            },
        },
    },
)
@api_view(["POST"])
def endOrder(request):
    try:
        order_id = request.data.get("order_id")
        if not order_id:
            return Response({"error": "Order ID is required."}, status=400)

        order = OrderItem.objects.get(id=order_id, active=True)
        order.end_time = timezone.now()
        order.active = False

        # Calculate actual usage time in minutes
        duration = (order.end_time - order.start_time).total_seconds() / 60
        expected_duration = int(
            order.price / 100 * 60
        )  # Derive expected duration from price

        if duration > expected_duration:
            extra_time = duration - expected_duration
            extra_five_min_blocks = (extra_time // 5) + (1 if extra_time % 5 else 0)
            interest = Decimal(0.04) * extra_five_min_blocks * order.price
            final_price = order.price + interest
        else:
            final_price = order.price

        order.price = final_price
        order.save()

        mpesa_callback = "https://crucial-perfect-horse.ngrok-free.app/cart/callback/"

        mpesa_client = MpesaClient()
        payment_no = request.data.get("payment_no")

        if not payment_no:
            return Response({"error": "Payment number is required."}, status=400)

        response = mpesa_client.make_stk_push(
            float(order.price), payment_no, mpesa_callback, "174379", "Pay for goods"
        )
        payment = Payment.objects.create(
            phone_no=payment_no, mpesa_transaction_id=response["CheckoutRequestID"]
        )
        print(response["CheckoutRequestID"])
        order.payment = payment
        order.save()
        return Response(
            {
                "message": "Order ended successfully.",
                "order_id": order.id,
                "final_price": str(order.price),
                "payment_status": "pending",
            },
            status=200,
        )

    except OrderItem.DoesNotExist:
        return Response({"error": "Order not found or already completed."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@extend_schema(
    operation_id="create_order_item",
    summary="Create order items",
    description="Create order items based on the provided data.",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "item": {"type": "integer", "example": 1},
                # "quantity": {"type": "integer", "example": 2},
            },
            # "required": ["item", "quantity"],
        }
    },
    responses={
        200: OpenApiResponse(description="Order item created successfully."),
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
    operation_id="get_bikes_order_duration",
    summary="Retrieve Order Duration for a Shop",
    description="Fetches the order duration details for a specific shop based on the provided item ID.",
    parameters=[
        OpenApiParameter(
            name="item",
            type=int,
            location=OpenApiParameter.QUERY,
            required=True,
            description="The item ID to filter order duration records.",
        )
    ],
    responses={200: OrderDurationSerializer(many=True)},
)
@api_view(["GET"])
def orderDuration(request):
    item_id = request.query_params.get("item")

    if not item_id:
        return Response({"error": "Item ID is required"}, status=400)

    try:
        # Retrieve the shop associated with the given item
        item = Item.objects.get(id=item_id)
        shop = item.shop  # Assuming `Item` model has a `shop` ForeignKey

        print(f"Shop ID is {shop.id}")

        # Get order durations for the shop
        durations = OrderDuration.objects.filter(shop=shop)
        serializer = OrderDurationSerializer(durations, many=True)

        return Response({"data": serializer.data})

    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)


@api_view(["POST"])
def mpesa_callback(request):
    print("Full Callback Data: %s", request.data)
    json_response = request.data.get("Body", {}).get("stkCallback", {})
    result_code = json_response.get("ResultCode")
    if result_code == 0:
        mpesa_transaction_id = json_response.get("CheckoutRequestID")
        print("Mpesa Transaction ID: %s", mpesa_transaction_id)
        try:
            data = Payment.objects.get(mpesa_transaction_id=mpesa_transaction_id)
            order = OrderItem.objects.get(payment=data.id)
            order.confirmed = True
            order.save()
            print("Order Confirmed: %s", order)
        except (Payment.DoesNotExist, OrderItem.DoesNotExist):
            return Response({"error": "Transaction or order not found"}, status=404)
    return Response(status=200)


# @extend_schema(
#     operation_id="delivered_orders",
#     summary="Retrieve delivered orders",
#     description="Retrieve all delivered orders.",
#     responses={
#         200: OpenApiResponse(description="List of delivered orders."),
#     },
# )
# @api_view(["GET"])
# def delivered(request):
#     order = Order.objects.all()
#     queryset = OrderItem.objects.all()
#     q1 = OrderItem.objects.filter(order=65)
#     serializer = OrderItemSerializer(q1, many=True)
#     confirmed = Order.objects.filter(confirmed=True)
#     serializer1 = OrderSerializer(confirmed, many=True)
#     return Response({"orders": serializer1.data})


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
        200: OpenApiResponse(description="Rating submitted successfully."),
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
        200: OpenApiResponse(description="List of user orders."),
    },
)
@api_view(["GET"])
def userOrder(request):
    user = request.account
    userOrders = OrderItem.objects.filter(account=user)
    orders = []
    o = 0
    for i in userOrders:
        # print("i am " +str(i))
        order_id = userOrders[o]
        serializer = OrderItemSerializer(order_id)
        # print(serializer.data)
        orders.append(serializer.data)

        o += 1
    return Response({"orders": orders})


# @extend_schema(
#     operation_id="end_lease",
#     summary="End lease for an order",
#     description="End the lease for a specific order.",
#     responses={
#         200: OpenApiResponse(description="Lease ended successfully."),
#         404: OpenApiResponse(
#             description="Order not found.",
#         ),
#     },
# )
# @api_view(["POST"])
# def end_lease(request, order_id):
#     try:
#         order = Order.objects.get(id=order_id)
#         order.end_time = timezone.now()  # Set the end time to the current time
#         order.save()
#         return Response(
#             {"message": "Lease ended successfully", "end_time": str(order.end_time)}
#         )
#     except Order.DoesNotExist:
#         return Response({"error": "Order not found"}, status=404)


@extend_schema(
    operation_id="time_spent",
    summary="Calculate time spent on an order",
    description="Calculate the time spent on a specific order.",
    responses={
        200: OpenApiResponse(description="Time spent calculated successfully."),
        404: OpenApiResponse(
            description="Order not found.",
        ),
    },
)
@api_view(["GET"])
def time_spent(request, order_id):
    try:
        order = OrderItem.objects.get(id=order_id)
        if order.end_time != None:
            time_spent = order.end_time - order.start_time
            return Response({"time_spent": str(time_spent)})
        time_spent = timezone.now() - order.start_time
        return Response({"time_spent": str(time_spent)})
    except OrderItem.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)


@extend_schema(
    request=None,  # No request body expected in Swagger
    responses={200: OrderItemSerializer(many=True)},
    summary="Update bike requires [can_update_item]",
)
@api_view(["POST"])
@has_perms(["can_update_bikes"], shop_required=True)
def shopOrders(request):
    orders = OrderItem.objects.filter(
        item__shop_id=request.validated_shop_id
    )  # Use filter to avoid exceptions

    serializer = OrderItemSerializer(orders, many=True)
    print(serializer.data)
    return Response({"data": serializer.data})  # Ensure the Response object is returned


@extend_schema(
    summary="Create an OrderDuration",
    description="API endpoint to create an OrderDuration entry. Requires `can_update_bikes` permission and a valid shop ID.",
    request={"application/json": {"example": {"time": 30, "price": "100.00"}}},
    responses={
        201: OpenApiResponse(
            description="OrderDuration created successfully.",
            examples=[
                {
                    "message": "OrderDuration created successfully.",
                    "id": 1,
                    "time": 30,
                    "price": "100.00",
                    "shop": 1,  # Shop ID auto-determined
                }
            ],
        ),
        400: OpenApiResponse(
            description="Bad Request - Invalid input.",
            examples=[
                {"error": "All fields (time, price) are required."},
                {"error": "Invalid price format."},
            ],
        ),
    },
)
@api_view(["POST"])
@has_perms(["can_update_bikes"], shop_required=True)
def create_order_duration(request):
    """
    API view to create an OrderDuration entry.
    """
    data = request.data

    # Validate required fields
    time = data.get("time")
    price = data.get("price")

    if not time or not price:
        return Response({"error": "All fields (time, price) are required."}, status=400)

    # Retrieve the shop from the logged-in user's context
    # shop = request.validated_shop_id  # This is set by @has_perms
    shop = Shop.objects.get(id=request.validated_shop_id)

    # Convert price to string (if needed)
    try:
        price = str(
            Decimal(price)
        )  # Ensure it can be converted to a valid numeric string
    except:
        return Response({"error": "Invalid price format."}, status=400)

    # Create OrderDuration instance
    order_duration = OrderDuration.objects.create(time=time, price=price, shop=shop)

    return Response(
        {
            "message": "OrderDuration created successfully.",
            "id": order_duration.id,
            "time": order_duration.time,
            "price": order_duration.price,
            "shop": order_duration.shop.id,  # Returned for reference
        },
        status=201,
    )
