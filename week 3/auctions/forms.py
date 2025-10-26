from django import forms
from .models import Listing

# =========================================
# 🧩 Django Form: NewItem
# This ModelForm is used to create a new Listing.
# It automatically maps form fields to the Listing model fields.
# =========================================

class NewItem(forms.ModelForm):
    """Form for creating a new auction listing."""

    class Meta:
        model = Listing
        fields = ('title', 'desc', 'img', 'category', 'start_bid')

        # Define custom input widgets for better UI control
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'desc': forms.Textarea(attrs={'class': 'form-control'}),
            'img': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'start_bid': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        # Define human-readable labels for form fields
        labels = {
            'title': 'Title',
            'desc': 'Description',
            'img': 'Image URL',
            'category': 'Category',
            'start_bid': 'Starting Bid',
        }


# =========================================
# 👨‍💻 Developer Information
# Author: Mohammad Hosein Habibi
# GitHub: @mandosein2025
# =========================================
