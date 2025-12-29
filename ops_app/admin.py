from django.contrib import admin
from .models import Position, Candidate, Voter, Vote


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("description", "maximumvote")
    search_fields = ("description",)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "position", "applied_at")
    search_fields = ("firstname", "lastname", "email")
    list_filter = ("status", "position")

    # custom field to display full name
    def name(self, obj):
        return f"{obj.firstname} {obj.lastname}"
    name.admin_order_field = "firstname"  # sorting support
    name.short_description = "Full Name"


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "voterid", "image")
    search_fields = ("firstname", "lastname", "voterid", "image")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "candidate")
    search_fields = ("voter", "candidate", "position")
