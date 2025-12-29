from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import Candidate, Vote, Position, Voter
from .forms import CandidateForm, PositionForm, VoterForm

# ---------------- HOME ----------------
def home(request):
    return render(request, 'home.html')


# ---------------- AUTH ----------------
def voter_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                messages.error(request, "Admins must login from the admin page.")
                return redirect("admin_login")
            else:
                auth_login(request, user)
                request.session.set_expiry(0)  # expires on browser close
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("voter_login")

    return render(request, "voter_login.html")


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            auth_login(request, user)
            request.session.set_expiry(0)
            messages.success(request, "Admin login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, "admin_login.html")


def register(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")  # voter or admin

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            password=password1,
            email=email,
            first_name=firstname,
            last_name=lastname
        )

        if role == "admin":
            user.is_staff = True
            user.is_superuser = True
            user.save()

        messages.success(request, f"Registration successful! Account created for {username}! Please log in.")
        return redirect("voter_login")

    return render(request, "register.html")


@login_required
def user_logout(request):
    """Logout user and redirect to correct login page"""
    is_admin = request.user.is_superuser  # store role before logout
    auth_logout(request)

    if is_admin:
        return redirect("home")
    else:
        return redirect("home")


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):
    """Redirect users to the correct dashboard based on role"""
    if request.user.is_superuser:
        return redirect("admin_dashboard")
    return redirect("voter_dashboard")


@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("voter_dashboard")

    total_positions = Position.objects.count()
    total_candidates = Candidate.objects.count()
    total_voters = User.objects.filter(is_superuser=False).count()
    voters_voted = Vote.objects.values("voter").distinct().count()

    def get_votes_for_position(position_name):
        candidates = Candidate.objects.filter(position__description=position_name)
        labels = [f"{c.firstname} {c.lastname}" for c in candidates]
        data = [Vote.objects.filter(candidate=c).count() for c in candidates]
        return {"labels": labels, "data": data}

    president_data = get_votes_for_position("President")
    vp_data = get_votes_for_position("Vice President")
    secretary_data = get_votes_for_position("Secretary")
    treasurer_data = get_votes_for_position("Treasurer")

    context = {
        "total_positions": total_positions,
        "total_candidates": total_candidates,
        "total_voters": total_voters,
        "voters_voted": voters_voted,
        "president_data": president_data,
        "vp_data": vp_data,
        "secretary_data": secretary_data,
        "treasurer_data": treasurer_data,
    }

    return render(request, "admin_dashboard.html", context)


@login_required
def voter_dashboard(request):
    try:
        voter = Voter.objects.get(user=request.user)
        return redirect('ballot_position')
    except Voter.DoesNotExist:
        voter = None

    if request.method == "POST":
        form = VoterForm(request.POST, request.FILES)
        if form.is_valid():
            voter = form.save(commit=False)
            voter.user = request.user
            voter.save()
            return redirect('ballot_position')
    else:
        form = VoterForm()

    return render(request, 'voter_dashboard.html', {'form': form, 'voter_exists': voter is not None})


# ---------------- VOTING ----------------
@login_required
def vote(request):
    if request.user.is_superuser:
        messages.error(request, "Admins cannot vote.")
        return redirect("admin_dashboard")

    if request.method == "POST":
        candidate_id = request.POST.get("candidate")

        try:
            candidate = Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            messages.error(request, "Invalid candidate selection.")
            return redirect("vote")

        if Vote.objects.filter(voter=request.user).exists():
            messages.error(request, "You have already voted!")
            return redirect("vote")

        Vote.objects.create(voter=request.user, candidate=candidate)
        candidate.vote_count += 1
        candidate.save()

        messages.success(request, "Your vote has been submitted successfully!")
        return redirect("result")

    candidates = Candidate.objects.all()
    return render(request, "vote.html", {"candidates": candidates})


@login_required
def result(request):
    candidates = Candidate.objects.all().order_by("-vote_count")
    return render(request, "result.html", {"candidates": candidates})


# ---------------- DATA VIEWS ----------------
def candidates(request):
    data = Candidate.objects.all()
    return render(request, "candidates.html", {"candidates": data})


def positions(request):
    data = Position.objects.all()
    return render(request, "positions.html", {"positions": data})


def voters(request):
    data = Voter.objects.all()
    return render(request, "voters.html", {"voters": data})


def votes(request):
    votes = Vote.objects.select_related("position", "candidate", "voter").order_by("position__description")
    return render(request, "votes.html", {"votes": votes})

# ---------------- CANDIDATE APPLY ----------------
def candidate_apply(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        manifesto = request.POST.get("manifesto")
        photo = request.FILES.get("photo")
        position_id = request.POST.get("position")


        try:
            position = Position.objects.get(id=position_id)
        except Position.DoesNotExist:
            messages.error(request, "Please select a valid position.")
            return redirect("candidate_apply")

        Candidate.objects.create(
            firstname=firstname,
            lastname=lastname,
            email=email,
            manifesto=manifesto,
            photo=photo,
            position=position,
            status="Pending"
        )
        messages.success(request, "Application submitted successfully!")
        return redirect("home")

    positions = Position.objects.all()
    return render(request, "candidate_apply.html", {"positions": positions})


# ---------------- BALLOT ----------------
def ballot_position(request):
    positions = Position.objects.prefetch_related(
        Prefetch(
            'candidate_set',
            queryset=Candidate.objects.filter(status="Approved"),
            to_attr="candidates"
        )
    )
    return render(request, "ballot_position.html", {"positions": positions})


def candidate_platform(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    return render(request, "candidate_platform.html", {"candidate": candidate})


def submit_vote(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate")
        # ✅ Your logic to save the vote here

        # Redirect to success page with context
        return render(request, "vote_success.html", {
            "message": "Ballot Submitted",
            "redirect_url": "/",  # Change to your home page URL
            "redirect_seconds": 30
        })

    # Show vote form if GET
    candidates = Candidate.objects.all()
    return render(request, "vote_form.html", {"candidates": candidates})

def vote_success(request):
    return render(request, "vote_success.html")


    


# ---------------- ADMIN CANDIDATES ----------------
@login_required
def candidates_admin(request):
    if not request.user.is_superuser:
        return redirect("voter_dashboard")

    candidates = Candidate.objects.all()
    return render(request, "candidates_admin.html", {"candidates": candidates})


@login_required

def approve_candidate(request, candidate_id):
    if not request.user.is_superuser:
        return redirect("voter_dashboard")

    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.status = "Approved"   # ✅ use lowercase consistently
    candidate.save()

    messages.success(request, f"{candidate.firstname} {candidate.lastname} has been approved!")
    return redirect("candidates_admin")

@login_required
def delete_candidate(request, candidate_id):
    if not request.user.is_superuser:
        return redirect("voter_dashboard")

    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.delete()
    messages.success(request, "Candidate deleted successfully.")
    return redirect("candidates_admin")


def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    if request.method == "POST":
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            return redirect("candidates_admin")
    else:
        form = CandidateForm(instance=candidate)
    return render(request, "edit_candidate.html", {"form": form, "candidate": candidate})



def reject_candidate(request, candidate_id):
    if not request.user.is_superuser:
        return redirect("voter_dashboard")

    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate.status = "Rejected"   # ✅ use lowercase consistently
    candidate.save()

    messages.error(request, f"{candidate.firstname} {candidate.lastname} has been rejected.")
    return redirect("candidates_admin")


def admin_ballot_positions(request):
    positions = Position.objects.all()
    return render(request, "admin_ballot_positions.html", {"positions": positions})
def candidate_detail(request, candidate_id):
    if not request.user.is_superuser:
        return redirect("voter_dashboard")

    candidate = get_object_or_404(Candidate, id=candidate_id)

    return render(request, "candidate_detail.html", {"candidate": candidate})
def add_position(request):
    if request.method == "POST":
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("positions")
    else:
        form = PositionForm()
    return render(request, "add_position.html", {"form": form})

def edit_position(request, pk):
    pos = get_object_or_404(Position, pk=pk)
    if request.method == "POST":
        form = PositionForm(request.POST, instance=pos)
        if form.is_valid():
            form.save()
            return redirect("positions")
    else:
        form = PositionForm(instance=pos)
    return render(request, "add_position.html", {"form": form, "edit": True})

def delete_position(request, pk):
    pos = get_object_or_404(Position, pk=pk)
    pos.delete()
    return redirect("positions")

def delete_voter(request, voter_id):
    voter = get_object_or_404(Voter, id=voter_id)
    voter.delete()
    messages.success(request, "Voter deleted successfully!")
    return redirect("voters")  # redirect back to voters list page
