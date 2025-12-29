from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('voter_login/', views.voter_login, name='voter_login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='user_logout'),  # updated to match template
    path('dashboard/', views.dashboard, name='dashboard'),  # unified dashboard redirect
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('voter_dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('vote/', views.vote, name='vote'),
    path('result/', views.result, name='result'),
    path('candidates_admin/',views.candidates_admin,name='candidates_admin'),
    path('positions/',views.positions,name='positions'),
    path('voters/',views.voters,name='voters'),
    path('votes/', views.votes, name='votes'),
    path("candidate_apply/", views.candidate_apply, name="candidate_apply"),
    path("admin_ballot_positions/", views.admin_ballot_positions, name="admin_ballot_positions"),
    path("ballot_position/", views.ballot_position, name="ballot_position"),
    path("candidate_platform/<int:candidate_id>/platform/", views.candidate_platform, name="candidate_platform"),
    path('submit_vote/', views.submit_vote, name='submit_vote'),
    path("approve_candidate/<int:candidate_id>/", views.approve_candidate, name="approve_candidate"),
    path("delete_candidate/<int:candidate_id>/", views.delete_candidate, name="delete_candidate"),
    path("reject_candidate/<int:candidate_id>/reject/", views.reject_candidate, name="reject_candidate"),
    path("edit_candidates/<int:candidate_id>/edit/", views.edit_candidate, name="edit_candidate"),
    path("candidate_detail/<int:candidate_id>/", views.candidate_detail, name="candidate_detail"),
    path("positions/add/", views.add_position, name="add_position"),
    path("positions/edit/<int:pk>/", views.edit_position, name="edit_position"),
    path("positions/delete/<int:pk>/", views.delete_position, name="delete_position"),
    path("vote_success/", views.vote_success, name="vote_success"),
    path("delete-voter/<int:voter_id>/", views.delete_voter, name="delete_voter"),
]



