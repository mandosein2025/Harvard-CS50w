from multiprocessing import context
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import User, Listing, Bid, Comment, Watchlist
from .forms import NewItem
from commerce.settings import LOGIN_REDIRECT_URL


# ==========================
# 🏠 INDEX PAGE
# ==========================
def index(request):
    """
    Display all active listings on the homepage.
    Each listing includes its highest bid and readable category name.
    """
    listings = Listing.objects.filter(active_status=True)

    # Attach category name and highest bid to each listing
    for item in listings:
        item.category = item.get_category_display()
        highest_amount_dict = item.bids.aggregate(Max('amount'))
        highest_amount = highest_amount_dict['amount__max']
        if highest_amount:
            item.bid = item.bids.get(amount=highest_amount)

    context = {'listings': listings}
    return render(request, "auctions/index.html", context)


# ==========================
# ⚠️ NOT FOUND PAGE
# ==========================
def not_found(request):
    """Render a custom 'Not Found' page."""
    return render(request, "auctions/notfound.html")


# ==========================
# 🔐 LOGIN
# ==========================
def login_view(request):
    """
    Handle user login process.
    If credentials are valid, user is logged in and redirected to index.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, 'Invalid username and/or password.')
            return redirect('login')

    return render(request, "auctions/login.html")


# ==========================
# 🚪 LOGOUT
# ==========================
def logout_view(request):
    """Log the user out and redirect to the homepage."""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


# ==========================
# 🧾 REGISTER
# ==========================
def register(request):
    """
    Register a new user account.
    Ensures that password and confirmation match, and username is unique.
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Validate password match
        if password != confirmation:
            messages.error(request, 'Passwords must match.')
            return redirect('register')

        # Try creating the new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, 'Username already taken.')
            return redirect('register')

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/register.html")


# ==========================
# 🆕 CREATE NEW LISTING
# ==========================
@login_required(login_url=LOGIN_REDIRECT_URL)
def new_listing(request):
    """
    Allow logged-in users to create a new listing.
    Validates the form before saving the new item.
    """
    if request.method == 'POST':
        form = NewItem(request.POST)
        if form.is_valid():
            user = request.user

            new = Listing(
                user=user,
                title=form.cleaned_data['title'],
                desc=form.cleaned_data['desc'],
                img=form.cleaned_data['img'],
                category=form.cleaned_data['category'],
                start_bid=form.cleaned_data['start_bid'],
            )
            new.save()

            messages.success(request, 'Listing added successfully.')
            return redirect('index')

        messages.error(request, 'Invalid form submission.')
        return redirect('newlisting')

    context = {'form': NewItem()}
    return render(request, "auctions/newlisting.html", context)


# ==========================
# 📄 LISTING DETAIL
# ==========================
@login_required(login_url=LOGIN_REDIRECT_URL)
def listing(request, list_id):
    """
    Display a single listing and handle actions like:
    - Add/remove from watchlist
    - Place a bid
    - Close the auction (owner only)
    - Add a comment
    """
    if request.user.is_authenticated:
        user = request.user

        # ======= POST REQUESTS =======
        if request.method == 'POST':

            # 📌 Add or remove from watchlist
            if 'watchlist' in request.POST:
                try:
                    listing = Listing.objects.get(pk=list_id)
                except Listing.DoesNotExist:
                    messages.error(request, 'Something went wrong. Try again.')
                    return redirect('listing', list_id=list_id)

                existing = user.watchlist.filter(list_id=listing)
                if existing.exists():
                    existing.delete()
                    messages.success(request, 'Listing removed from watchlist.')
                else:
                    Watchlist.objects.create(user_id=user, list_id=listing)
                    messages.success(request, 'Listing added to watchlist.')

                return redirect('listing', list_id=list_id)

            # 💰 Place a new bid
            elif 'bid' in request.POST:
                bid_amount = request.POST.get('bid_amount')

                if not bid_amount:
                    messages.error(request, 'Enter a valid bid amount.')
                    return redirect('listing', list_id=list_id)

                listing = Listing.objects.get(pk=list_id)

                # Get highest bid so far
                highest_amount = listing.bids.aggregate(Max('amount'))['amount__max']

                # Validate the bid
                if highest_amount:
                    if int(highest_amount) >= int(bid_amount):
                        messages.error(request, 'Bid must be higher than current bid.')
                        return redirect('listing', list_id=list_id)
                else:
                    if int(listing.start_bid) > int(bid_amount):
                        messages.error(request, 'Bid must be at least the starting bid.')
                        return redirect('listing', list_id=list_id)

                # Save the new bid
                Bid.objects.create(list_id=listing, user_id=user, amount=bid_amount)
                messages.success(request, 'Bid placed successfully.')
                return redirect('listing', list_id=list_id)

            # 🔒 Close the auction (owner only)
            elif 'close' in request.POST:
                listing = Listing.objects.get(pk=list_id)
                if user.id != listing.user.id:
                    messages.error(request, 'Only the owner can close this listing.')
                    return redirect('listing', list_id=list_id)

                # Remove from all watchlists
                listing.watchlisted.all().delete()

                # Determine winner
                highest_amount_dict = listing.bids.aggregate(Max('amount'))
                highest_amount = highest_amount_dict['amount__max']
                if highest_amount:
                    highest_bid = listing.bids.get(amount=highest_amount)
                    listing.winner = highest_bid.user_id
                else:
                    listing.winner = None  # Safe fallback if no bids exist

                listing.active_status = False
                listing.save()

                messages.success(request, 'Listing closed successfully.')
                return redirect('listing', list_id=list_id)

            # 💬 Add a comment
            elif 'comment' in request.POST:
                comment_text = request.POST.get('usercomment')
                listing = Listing.objects.get(pk=list_id)
                Comment.objects.create(list_id=listing, user_id=user, comment=comment_text)
                messages.success(request, 'Comment added successfully.')
                return redirect('listing', list_id=list_id)

        # ======= GET REQUEST =======
        try:
            listing = Listing.objects.get(pk=list_id)
        except Listing.DoesNotExist:
            return redirect('not_found')

        # Check if item is in watchlist
        watchlisted = Watchlist.objects.filter(list_id=listing, user_id=user).exists()

        # Get readable category name
        listing.category = listing.get_category_display()

        # Get current highest bid
        highest_amount = listing.bids.aggregate(Max('amount'))['amount__max']
        if highest_amount:
            listing.bid = listing.bids.get(amount=highest_amount)

        # Get total number of bids and comments
        count = listing.bids.count()
        comments = listing.list_comments.all()

        context = {
            'listing': listing,
            'count': count,
            'user': user,
            'comments': comments,
            'watchlisted': watchlisted,
        }

        return render(request, "auctions/listing.html", context)


# ==========================
# 👁 USER WATCHLIST
# ==========================
@login_required(login_url=LOGIN_REDIRECT_URL)
def watchlist(request):
    """
    Display all listings currently in the user's watchlist.
    """
    user = request.user
    listings = user.watchlist.all()

    # Attach highest bid for each listing in watchlist
    for item in listings:
        highest_amount_dict = item.list_id.bids.aggregate(Max('amount'))
        highest_amount = highest_amount_dict['amount__max']
        if highest_amount:
            item.list_id.bid = item.list_id.bids.get(amount=highest_amount)

    context = {'listings': listings}
    return render(request, "auctions/watchlist.html", context)


# ==========================
# 🧩 CATEGORY LIST
# ==========================
def category(request):
    """Display all available listing categories."""
    categories = Listing.category.field.choices
    context = {'categories': categories}
    return render(request, "auctions/category.html", context)


# ==========================
# 🗂 CATEGORY DETAIL
# ==========================
def category_type(request, cat):
    """
    Display all active listings belonging to a specific category.
    """
    listings = Listing.objects.filter(category=cat, active_status=True)
    category_name = [c[1] for c in Listing.category.field.choices if c[0] == cat][0]

    context = {
        'listings': listings,
        'category': category_name
    }
    return render(request, "auctions/category_listing.html", context)


# =========================================
# 👨‍💻 Developer Information
# Author: Mohammad Hosein Habibi
# GitHub: @mandosein2025
# =========================================