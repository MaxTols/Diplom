from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .tasks import send_msg_task

from .models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    Order,
    OrderItem,
    Contact,
    ConfirmEmailToken,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    fieldsets = (
        (None, {"fields": ("email", "password", "type")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("email", "first_name", "last_name", "is_staff")


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "url",
        "user",
        "status",
    ]
    list_filter = ["status"]
    search_fields = [
        "name",
        "user__first_name",
        "user__last_name",
    ]


class ShopInline(admin.TabularInline):
    model = Shop.categories.through
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [ShopInline]
    list_display = [
        "name",
    ]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
    ]
    search_fields = ["name"]


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 0
    fields = ("parameter", "value")
    readonly_fields = ("parameter", "value")


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    inlines = [ProductParameterInline]
    list_display = [
        "product",
        "model",
        "shop",
        "quantity",
        "price",
        "price_rrc",
    ]
    search_fields = ["product__name"]


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    pass
    list_display = [
        "product_info",
        "parameter",
        "value",
    ]
    search_fields = ["product_info__model"]


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0
    fields = (("product_info", "quantity"),)
    readonly_fields = ("product_info", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ("id", "status", ("user", "contact"))
    readonly_fields = ("id", "user", "contact")
    list_display = ("id", "user", "status", "dt")
    list_filter = ("user", "status", "dt")
    inlines = [
        OrderItemInline,
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        rus_state = ""
        for state_tuple in Order.Status:
            if state_tuple[0] == obj.status:
                rus_state = state_tuple[1]
                break

        title = f"Обновление статуса заказа {obj.id}"
        message = f"Заказ {obj.id} получил статус {rus_state}."
        addressee_list = [obj.user.email]
        send_msg_task.delay(title, message, addressee_list)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "product_info",
        "quantity",
    ]
    search_fields = ["order__dt"]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "city",
        "street",
        "house",
        "building",
        "structure",
        "apartment",
    ]
    list_filter = ["city"]
    search_fields = [
        "user__last_name",
        "user_first_name",
    ]


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "key",
        "created_at",
    ]
