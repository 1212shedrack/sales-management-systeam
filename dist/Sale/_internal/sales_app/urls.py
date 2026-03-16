from django.urls import path
from . import views
app_name = "sales_app"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # 🛒 Product management
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:pk>/", views.view_product, name="view_product"),
    path("products/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path(
        "products/<int:pk>/delete/",
        views.delete_product,
        name="delete_product"
    ),
    path("products/", views.product_list, name="product_list"),

    # 💰 Sales
    path("sales/", views.view_sales, name="view_sales"),
    path("sales/record/", views.record_sale, name="record_sale"),
    path(
        "sales/print/<int:sale_id>/",
        views.print_receipt,
        name="print_receipt"
    ),
    path(
        "sales/download/<int:sale_id>/",
        views.download_receipt,
        name="download_receipt"
    ),
    path("sales/delete/<int:sale_id>/", views.delete_sale, name="delete_sale"),
    path('reports/', views.sales_report, name='reports'),

    # ⚙️ Management
    path("reports/", views.reports, name="reports"),
    path("customers/", views.customers, name="customers"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path("expenses/", views.expenses, name="expenses"),
    path("settings/", views.settings_view, name="settings"),

]
