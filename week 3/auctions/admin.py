from django.contrib import admin
from . import models

# =========================================
# ⚙️ Django Admin Configuration
# This file registers all models with the Django admin site
# so they can be managed through the web interface.
# =========================================


# Registering each model with the admin panel
# so that an admin user can view, add, edit, and delete entries.

admin.site.register(models.User)       # Custom User model
admin.site.register(models.Listing)    # Auction Listings
admin.site.register(models.Bid)        # Bids on Listings
admin.site.register(models.Comment)    # User Comments on Listings
admin.site.register(models.Watchlist)  # Watchlist items for each user


# =========================================
# 👨‍💻 Developer Information
# Author: Mohammad Hosein Habibi
# GitHub: @mandosein2025
# =========================================
