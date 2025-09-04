from django.urls import path

from . import api_views as views

## URLs for app API endpoints that live under /api/v<version>/<app>/

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'transactions', views.TransactionViewSet, basename='credit_accounting')

urlpatterns = [
    ## API endpoints
    # path('', include(router.urls)),
    path("accounts/", views.AccountListView.as_view()),
    path("transactions/", views.TransactionListView.as_view()),
    path("transactions/filter/", views.TransactionListFilterView.as_view()),
    path("settings/", views.SettingsView.as_view()),
    path("pos/transaction/", views.PosTransactionView.as_view()),
    path("pos/accounts/", views.PosAccountsView.as_view()),
    path("pos/account/", views.PosAccountView.as_view()),
]
