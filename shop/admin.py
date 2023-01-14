from django.contrib import admin

# Register your models here.
from .models import Porduct, Contact, Orders, OrderUpdate

admin.site.register(Porduct)
admin.site.register(Orders)
admin.site.register(Contact)
admin.site.register(OrderUpdate)
