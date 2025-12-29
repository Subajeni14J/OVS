import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Position(models.Model):
    """Election positions (e.g., President, Vice President, Secretary, Treasurer)."""
    description = models.CharField(max_length=100, unique=True)
    maximumvote = models.IntegerField(default=1)

    def __str__(self):
        return self.description


class Candidate(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    manifesto = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    applied_at = models.DateTimeField(default=timezone.now)  # ✅ FIXED
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to="candidates/", null=True, blank=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname} - {self.position.description} ({self.status})"


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    voterid = models.CharField(max_length=20, unique=True, editable=False)
    image = models.ImageField(upload_to='voter_images/', blank=True, null=True, default='default.png')
    def save(self, *args, **kwargs):
        if not self.voterid:
            last_voter = Voter.objects.order_by('-id').first()
            if last_voter and last_voter.voterid.startswith("VOTER-"):
                last_number = int(last_voter.voterid.split('-')[1])
                self.voterid = f"VOTER-{last_number+1:04d}"
            else:
                self.voterid = "VOTER-0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.voterid})"


class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    class Meta:
        unique_together = ("voter", "position")  # prevents duplicate votes per position


    def __str__(self):
        return f"{self.voter.username} voted {self.candidate.firstname} {self.candidate.lastname}"
