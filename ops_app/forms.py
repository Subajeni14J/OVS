from django import forms
from .models import Candidate, Position, Voter

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ["position", "photo", "firstname", "lastname", "manifesto"]
class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ["description", "maximumvote"]
class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ['firstname', 'lastname', 'image']


