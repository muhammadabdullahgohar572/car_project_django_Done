from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .models import Car, Bid
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from django.utils.timezone import make_aware
from datetime import datetime  
def Homepage(request):
    car_data = Car.objects.all()
    return render(request, "Home.html", {"car_data": car_data})

def Register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("Home_page")
    else:
        form = UserCreationForm()
    return render(request, "Register.html", {"form": form})

def Login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("Home_page")
    else:
        form = AuthenticationForm()
    return render(request, "Login.html", {"form": form})  

def Logout(request):
    logout(request)
    return redirect("Home_page")



@login_required
def AddCar(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        started_bid = request.POST.get("started_bid")
        end_auction_str = request.POST.get("end_auction")
        image = request.FILES.get("image")
        
        try:
            # Convert string to datetime object
            end_auction = datetime.strptime(end_auction_str, "%Y-%m-%dT%H:%M")
            end_auction = make_aware(end_auction)  # Make timezone aware
            
            Car.objects.create(
                title=title,
                description=description,
                started_bid=started_bid,
                current_bid=started_bid,
                end_auction=end_auction,
                image=image,
                owner=request.user
            )
            messages.success(request, "Car added successfully to auction!")
            return redirect("Home_page")
        except ValueError as e:
            messages.error(request, f"Invalid date format: {str(e)}")
        except Exception as e:
            messages.error(request, f"Error adding car: {str(e)}")
    
    return render(request, "Addcar.html")



@login_required
def ShowDetalis(request, id):
    car = get_object_or_404(Car, id=id)
    bids = car.bids.all().order_by('-amount')
    
    # Check auction status
    if now() > car.end_auction:
        car.is_auction_active = False
        if bids.exists():
            car.winner = bids.first().bidder
        car.save()
    
    if request.method == "POST":
        if not car.is_auction_active:
            messages.error(request, "The auction has ended. No more bids are accepted")
        else:
            try:
                amount = float(request.POST.get("amount"))
                if amount <= car.current_bid:
                    messages.error(request, f"Your bid must be higher than ${car.current_bid:.2f}")
                else:
                    Bid.objects.create(
                        amount=amount,
                        car=car,
                        bidder=request.user
                    )
                    car.current_bid = amount
                    car.save()
                    messages.success(request, "Bid placed successfully!")
            except (ValueError, TypeError):
                messages.error(request, "Invalid bid amount")
        
        return redirect("ShowDetalis", id=id)
    
    context = {
        "car": car,
        "bids": bids,
        "is_auction_active": car.is_auction_active,
        "winner": car.winner  # Make sure to pass the winner to template
    }
    return render(request, "ShowDeatils.html", context)