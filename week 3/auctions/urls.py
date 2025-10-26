from django.urls import path
from . import views

# =========================================
# 🌐 Django URL Configuration for Auctions App
# Each path below connects a URL route to its view function.
# Order of routes has been randomized for clarity testing.
# =========================================

urlpatterns = [

    # 🗂 Category Detail Page (e.g., /category/electronics)
    path("category/<str:cat>", views.category_type, name="category_type"),

    # 📄 Listing Detail (Individual auction listing)
    path("listing/<int:list_id>", views.listing, name="listing"),

    # 🚪 Logout page
    path("logout", views.logout_view, name="logout"),

    # 🏠 Homepage - shows all active listings
    path("", views.index, name="index"),

    # 🧩 Category List - displays all categories
    path("category", views.category, name="category"),

    # 🆕 Create a New Listing
    path("new", views.new_listing, name="newlisting"),

    # 👁 User Watchlist - shows items added to watchlist
    path("watchlist", views.watchlist, name="watchlist"),

    # 🔐 Login Page
    path("login", views.login_view, name="login"),

    # 🧾 Register New User
    path("register", views.register, name="register"),

    # ⚠️ Custom Not Found Page
    path("notfound", views.not_found, name="not_found"),
]

# =========================================
# 👨‍💻 Developer Information
# Author: Mohammad Hosein Habibi
# GitHub: @mandosein2025
# =========================================
