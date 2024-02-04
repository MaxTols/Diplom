from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.db.models import Sum, F, Q
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import (
    Shop,
    Category,
    Product,
    ProductInfo,
    Contact,
    ConfirmEmailToken,
    Order,
    OrderItem,
)
from .serializers import (
    CategorySerializer,
    ShopSerializer,
    ProductSerializer,
    ProductInfoSerializer,
    ContactSerializer,
    UserSerializer,
    OrderSerializer,
    OrderItemSerializer,
)
from .tasks import send_msg_task, import_data_task


class RegisterUserView(APIView):
    def post(self, request, *args, **kwargs):
        if not {
            "first_name",
            "last_name",
            "email",
            "password",
            "username",
            "phone",
        }.issubset(request.data):
            return Response("Not added all arguments", status=400)

        try:
            validate_password(request.data["password"])

        except Exception as password_error:
            return Response({"password": str(password_error)}, status=400)

        else:
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data["password"])
                user.save()

                token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user.id)
                subject = f"Password token for {token.user.email}"
                body = token.key
                to_email = [token.user.email]
                send_msg_task.delay(subject, body, to_email)
                return Response("User is registered", status=201)

            else:
                return Response(user_serializer.errors, status=400)


class ConfirmUserView(APIView):
    def post(self, request, *args, **kwargs):
        if not {"email", "token"}.issubset(request.data):
            return Response("No added all arguments", status=400)

        token = ConfirmEmailToken.objects.filter(
            user__email=request.data["email"], key=request.data["token"]
        ).first()
        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return Response("User is confirmed")

        else:
            return Response("Incorrectly token or email", status=400)


class LoginAccountView(APIView):
    def post(self, request, *args, **kwargs):
        if not {"email", "password"}.issubset(request.data):
            return Response("No added all arguments", status=400)

        user = authenticate(
            request, email=request.data["email"], password=request.data["password"]
        )
        if user is not None:
            if user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"Token": token.key})

        return Response("Incorrectly data", status=400)


class AccountDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        user_serializer = UserSerializer(request.user)
        return Response(user_serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if "password" in request.data:
            try:
                validate_password((request.data["password"]))
            except Exception as password_error:
                return Response({"password": password_error}, status=400)

            else:
                request.user.set_password(request.data["password"])

        user_serializer = UserSerializer(request.user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response("Account details is updated")
        else:
            return Response(user_serializer.errors, status=400)


class ContactView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if not {"city", "street", "house"}.issubset(request.data):
            return Response("No added all contacts", status=400)

        request.data.update({"user": request.user.id})
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        contact_id = request.data.get("contact_id")
        contact = Contact.objects.filter(id=contact_id, user_id=request.user.id).first()
        if contact:
            request.data.update({"user": request.user.id})
            serializer = ContactSerializer(contact, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response("Contact is updated")
            else:
                return Response(serializer.errors, status=400)
        return Response("No such contact", status=400)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        contact_id = request.data.get("contact_id")
        contact = Contact.objects.filter(
            id=contact_id, user_id=request.user.id
        ).delete()
        if contact[0]:
            serializer = ContactSerializer(contact, data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response("Contact is deleted")
        return Response("No such contact", status=400)


class SellerOrdersView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if request.user.type != "SP":
            return Response("Only shop", status=403)

        order = (
            Order.objects.filter(
                order_items__product_info__shop__user_id=request.user.id
            )
            .exclude(status="BT")
            .prefetch_related(
                "order_items__product_info__product__category",
                "order_items__product_info__product_parameters__parameter",
            )
            .annotate(
                total_sum=Sum(
                    F("order_items__quantity") * F("order_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)


class SellerStatusView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if request.user.type != "SP":
            return Response("Only shop", status=403)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if request.user.type != "SP":
            return Response("Only shop", status=403)

        shop = Shop.objects.filter(user_id=request.user.id)
        status_dict = {"CL": "OP", "OP": "CL"}
        for item in shop:
            status, name = item.status, item.name
            status_reverse = status_dict[status]
            Shop.objects.filter(user_id=request.user.id).update(status=status_reverse)
            return Response(f"Status {name} is {status_reverse}")


class SellerUpdate(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if request.user.type != "SP":
            return Response("Only shop", status=403)

        url = request.data.get("url")
        if url:
            import_data_task.delay(url=url, user_id=request.user.id)
            return Response("Data is updated")

        return Response("No added all arguments", status=400)


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductInfoView(ListAPIView):
    def get(self, request, *args, **kwargs):
        shop_id = request.GET.get("shop_id")
        product_id = request.GET.get("product_id")
        list_id = {"shop_id": shop_id, "product_id": product_id}
        for key, value in list_id.items():
            if value is None:
                return Response(f"Not added {key}")

        queryset = (
            ProductInfo.objects.filter(shop_id=shop_id, product_id=product_id)
            .select_related("shop", "product__category")
            .prefetch_related("product_parameters__parameter")
            .distinct()
        )
        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


class BasketView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        basket = (
            Order.objects.filter(user_id=request.user.id, status="BT")
            .prefetch_related(
                "order_items__product_info__product__category",
                "order_items__product_info__product_parameters__parameter",
            )
            .annotate(
                total_sum=Sum(
                    F("order_items__quantity") * F("order_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        items = request.data.get("items")
        if not items:
            return Response("No added all arguments", status=400)

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, status="BT")
        obj_created = 0
        for item in items:
            item.update({"order": basket.id})
            serializer = OrderItemSerializer(data=item)
            if serializer.is_valid():
                try:
                    serializer.save()
                except IntegrityError as error:
                    return Response({"Errors": str(error)}, status=400)
                else:
                    obj_created += 1
            else:
                return Response(serializer.errors, status=400)

        return Response(f"Created {obj_created} objects")

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        items = request.data.get("items")
        if items:
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id, status="BT"
            )
            obj_updated = 0
            for item in items:
                if type(item["id"]) == int and type(item["quantity"]) == int:
                    obj_updated += OrderItem.objects.filter(
                        order_id=basket.id, id=item["id"]
                    ).update(quantity=item["quantity"])
            return Response(f"Updated {obj_updated} objects")

        return Response("No added all arguments", status=400)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        items = request.data.get("items")
        if items:
            items_list = items.split(",")
            basket, _ = Order.objects.get_or_create(
                user_id=request.user.id, status="BT"
            )
            query = Q()
            obj_deleted = False
            for item_id in items_list:
                if item_id.isdigit():
                    query = query | Q(order_id=basket.id, id=item_id)
                    obj_deleted = True

            if obj_deleted:
                del_count = OrderItem.objects.filter(query).delete()[0]
                return Response(f"Deleted {del_count} objects")

        return Response("No added all arguments", status=400)


class OrderView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        order = (
            Order.objects.filter(user_id=request.user.id)
            .exclude(status="BT")
            .prefetch_related(
                "order_items__product_info__product__category",
                "order_items__product_info__product_parameters__parameter",
            )
            .annotate(
                total_sum=Sum(
                    F("order_items__quantity") * F("order_items__product_info__price")
                )
            )
            .distinct()
        )
        serializer = OrderSerializer(order, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response("Log in required", status=403)

        if request.user.type != "SP":
            return Response("Only shop", status=403)

        if not {"id", "contact"}.issubset(request.data):
            return Response("No added all arguments", status=400)

        try:
            is_updated = Order.objects.filter(
                user_id=request.user.id, id=request.data["id"]
            ).update(contact_id=request.data["contact"], status="CR")
        except IntegrityError:
            return Response("Incorrect arguments", status=400)

        else:
            if is_updated:
                subject = "Updating the order status"
                body = f"The order {request.data['id']} has been formed"
                to_email = [request.user.email]
                send_msg_task.delay(subject, body, to_email)
                return Response("Order is created")
