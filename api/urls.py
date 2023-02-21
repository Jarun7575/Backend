from django.urls import include, path
from .views import AccountView


urlpatterns = [
    path("account", AccountView.as_view()),
    path("account/login", AccountView.login),
	path('account/addaccount', AccountView.addaccount),
	path('account/addleave', AccountView.addleave),
    path('account/getuser', AccountView.getuser),
	path('account/getuserleaves', AccountView.getuserleaves),
	path('account/getallleaves', AccountView.getallleaves),
	path('account/updateleave', AccountView.updateleave),
	path('account/deleteleave', AccountView.deleteleave)
]
