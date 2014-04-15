
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from hamptons.models import Hamptonian, Frampton

class HamptonianAdministration(UserAdmin):
    pass

#admin.site.unregister(User)
admin.site.register(Hamptonian, HamptonianAdministration)
admin.site.register(Frampton)