from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.utils.timezone import now  # Add this import

class Car(models.Model):
    title = models.CharField(max_length=100) 
    description = models.TextField()
    image = CloudinaryField('image')
    started_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    end_auction = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='won_auctions')
    is_auction_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.owner}-{self.title}'
    
    def save(self, *args, **kwargs):
        # Update auction status based on end time
        if now() > self.end_auction:
            self.is_auction_active = False
        super().save(*args, **kwargs)

class Bid(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.car} - {self.bidder} - {self.amount}'