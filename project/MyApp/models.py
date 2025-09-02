from django.db import models
from django.contrib.postgres.indexes import HashIndex

class Services(models.Model):
    ServiceName = models.CharField(max_length=255)

    def __str__(self):
        return self.ServiceName

class Userr(models.Model):
    FullName = models.CharField(max_length=255)
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=128)
    TypeOfService = models.ForeignKey(Services, on_delete=models.CASCADE)
    PhoneNumber = models.CharField(null=True, blank=True)
    YearsOfExperience = models.IntegerField(null=True, blank=True)
    Location = models.CharField(null=True, blank=True)
    img = models.ImageField(upload_to='UserImg', null=True, blank=True)
    IsNotifications = models.BooleanField(default=True)
    IsServices = models.BooleanField(default=True)

    class Meta:
        indexes = [
            HashIndex(fields=['id'], name='id_hash_idx'),
            HashIndex(fields=['Email'], name='email_hash_idx'),
        ]


class UserRating(models.Model):
    UserId = models.ForeignKey(Userr, on_delete=models.CASCADE)
    Evaluation = models.FloatField()

    def __str__(self):
        return f'{self.UserId} - {self.Evaluation}'


class Notifications(models.Model):
    UserId = models.ForeignKey(Userr, on_delete=models.CASCADE)
    Title = models.CharField(max_length=255)
    Description = models.CharField(max_length=500)
    Isrequest = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.Title} - {self.UserId}'


class ServiceRequest(models.Model):
    IdUser = models.ForeignKey(Userr, on_delete=models.CASCADE, related_name='requests_made')
    IdClient = models.ForeignKey(Userr, on_delete=models.CASCADE, related_name='requests_received')
    Location = models.CharField()
    HourlyPrice = models.IntegerField()
    ClientOrderStatus = models.IntegerField(default=0)
    

    def __str__(self):
        return f'{self.IdUser} -> {self.IdClient} ({self.HourlyPrice})'



class EmailCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)