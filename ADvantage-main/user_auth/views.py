from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
import random
from django.core.mail import send_mail
from .models import AdRequest
from .forms import AdRequestForm
import logging
import os
from django.conf import settings 
import subprocess
from manage_cust.models import Customer                 # NEW
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from manage_cust.models import Customer
from .models            import AdRequest
from django.shortcuts           import render, redirect, get_object_or_404
from django.contrib             import messages
from AD_gen.google_trends       import scrape_daily_trends
from .models                    import AdRequest
from AD_gen.google_trends_7d import scrape_daily_trends_7d
from manage_cust.utils import send_email, send_emails_from_csv
from manage_cust.models import Customer
from django.db.models import Count
from django.contrib.auth import get_user_model

from .models import AdRequest
from manage_cust.models import Customer, SentEmail
from django.db.models import Count, Sum, F, ExpressionWrapper, IntegerField
from django.db.models.functions import Cast
import sys
import logging, os, subprocess, sys
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import AdRequestForm
from django.shortcuts import render, redirect
import pprint   # add at top if not there already
import csv
from io import StringIO
from django.http import HttpResponse


logger = logging.getLogger(__name__)
User = get_user_model()

def signup(request):
    if request.method == "POST":
        request.session.flush()  # ✅ Clear old session data before signup

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        if not email:
            return render(request, "user_auth/signup.html", {"error": "Email is required"})

        if User.objects.filter(email=email).exists():
            messages.error(request, "User already exists. Please log in.")
            return redirect("login")  # ✅ Redirect to login if user exists

        # ✅ Create user without password (password will be set in reset-password)
        user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
        request.session["user_id"] = user.id  # ✅ Store user ID for password setup

        return redirect("reset-password")  # ✅ Redirect to set password

    return render(request, "user_auth/signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        print(f"DEBUG: Attempting login for {email} with password {password}")
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            print(f"DEBUG: Authentication successful for {email}")
            login(request, user)
            return redirect("dashboard")  # or redirect wherever you need
        else:
            print(f"DEBUG: Authentication failed for {email}")
            messages.error(request, "Invalid login credentials")
            return redirect("sign_in_error")
            
    return render(request, "user_auth/login.html")


def password_reset(request):
    """
    This view handles password reset after signup.
    Users are redirected here after signing up to set their password.
    """
    if request.method == "POST":
        user_id = request.session.get("user_id")

        if not user_id:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect("signup")  # Redirect to signup if session expires

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please sign up again.")
            return redirect("signup")  # Redirect to signup if user not found

        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            request.session["password_reset_failed"] = True  
            return redirect("update-pw-error")  # Redirect to error page

        # Reset Password
        user.set_password(new_password)
        user.save()

        # Explicitly set authentication backend if multiple backends exist
        user.backend = "django.contrib.auth.backends.ModelBackend"

        # Log in user after password reset
        login(request, user, backend=user.backend)

        return redirect("login")  # Redirect to login instead of signup

    return render(request, "user_auth/reset_password.html")


def update_pw_error(request):
    """
    This view handles the password reset when users enter mismatched passwords.
    It allows them to retry without restarting the process.
    """
    user_id = request.session.get("user_id") 

    if not user_id:
        messages.error(request, "Session expired. Please request a new OTP.")
        return redirect("forgot-password")  

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect("update-pw-error")  

        try:
            user = User.objects.get(id=user_id)

            # Reset Password
            user.set_password(password1)
            user.save()

            # Do NOT flush session immediately (retain messages)
            messages.success(request, "Password updated successfully! Please log in.")
            
            return redirect("login")  # Redirect to login page instead of signup

        except User.DoesNotExist:
            messages.error(request, "User not found. Please sign up again.")
            return redirect("signup")  

    return render(request, "user_auth/update_pw_error.html")




def forgot_password(request):
    """
    This view handles 'Forgot Password' functionality.
    Users will enter their email and receive an OTP to reset their password.
    """
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session["otp"] = otp
            request.session["reset_email"] = email  

            subject = "🔐 Reset Your Password - ADvantage"
            message = f"""
                Dear {user.first_name},

                We received a request to reset your password for your ADvantage account. 
                Please use the One-Time Password (OTP) below to proceed:

                🔢 YOUR OTP: {otp} 

                This OTP is valid for the next 10 minutes. If you did not request a password reset, 
                please ignore this email, and your account will remain secure.

                About ADvantage:  
                ADvantage is an AI-powered ad generation platform that helps businesses create 
                engaging and personalized advertisements using the latest trends and data.  

                If you have any questions, feel free to reach out to our support team.

                Best regards,  
                The ADvantage Team  
                advantage.bluemelon@gmail.com  
            """


            send_mail(
                subject,
                message,
                "advantage.bluemelon@gmail.com",  # Your sender email
                [email],
                fail_silently=False,
            )

            return redirect("forgotpw-otp")  # ✅ Redirect to reset-password form
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect("forgotpw-email-error")  

    return render(request, "user_auth/forgot_password.html")


def forgotpw_emailerror(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session["otp"] = otp
            request.session["reset_email"] = email  

            print(f"DEBUG: Email found, OTP {otp} stored for {email}")  # ✅ Check if session is stored

            subject = "🔐 Reset Your Password - ADvantage"
            message = f"""
                Dear {user.first_name},

                We received a request to reset your password for your ADvantage account. 
                Please use the One-Time Password (OTP) below to proceed:

                🔢 YOUR OTP: {otp} 

                This OTP is valid for the next 10 minutes. If you did not request a password reset, 
                please ignore this email, and your account will remain secure.

                About ADvantage:  
                ADvantage is an AI-powered ad generation platform that helps businesses create 
                engaging and personalized advertisements using the latest trends and data.  

                If you have any questions, feel free to reach out to our support team.

                Best regards,  
                The ADvantage Team  
                advantage.bluemelon@gmail.com  
            """

            send_mail(
                subject,
                message,
                "advantage.bluemelon@gmail.com",  
                [email],
                fail_silently=False,
            )

            print("DEBUG: Email sent successfully")  # ✅ Check if email is sent

            return redirect("forgotpw-otp")  # ✅ Redirect to OTP page

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            print("DEBUG: No account found for email")  # ✅ Debug missing user
            return render(request, "user_auth/forgotpw_emailerror.html")  

    return render(request, "user_auth/forgotpw_emailerror.html")




def forgotpw_otp(request):
    if request.method == "POST":
        otp_entered = ''.join([request.POST.get(f"otp{i}") for i in range(1, 7)])
        stored_otp = str(request.session.get("otp"))
        email = request.session.get("reset_email")  

        if otp_entered == stored_otp:
            try:
                user = User.objects.get(email=email)
                request.session["user_id"] = user.id  # ✅ Store user ID in session
                return redirect("reset-password")  # ✅ Redirect to password reset page
            except User.DoesNotExist:
                messages.error(request, "User not found. Please sign up again.")
                return redirect("signup")

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("otp-error")  

    return render(request, "user_auth/forgotpw_otp.html")


def otp_error(request):
    if request.method == "POST":
        otp_entered = ''.join([request.POST.get(f"otp{i}") for i in range(1, 7)])
        stored_otp = str(request.session.get("otp"))
        email = request.session.get("reset_email")  

        if otp_entered == stored_otp:
            try:
                user = User.objects.get(email=email)
                request.session["user_id"] = user.id  # ✅ Store user ID in session
                return redirect("reset-password")  # ✅ Redirect to password reset
            except User.DoesNotExist:
                messages.error(request, "User not found. Please sign up again.")
                return redirect("signup")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("otp-error")  # ✅ Stay on the same page if incorrect

    return render(request, "user_auth/otp_error.html")




def resend_otp(request):
    """
    Resends OTP without requiring the user to re-enter their email.
    """
    email = request.session.get("reset_email")

    if not email:
        return redirect("forgot-password")  # Redirect if session expired

    try:
        user = User.objects.get(email=email)
        otp = random.randint(100000, 999999)
        request.session["otp"] = otp  # Store new OTP

        subject = "🔐 New OTP for Password Reset - ADvantage"
        message = f"""
                Dear {user.first_name},

                We received a request to reset your password for your ADvantage account. 
                Please use the One-Time Password (OTP) below to proceed:

                🔢 YOUR OTP: {otp} 

                This OTP is valid for the next 10 minutes. If you did not request a password reset, 
                please ignore this email, and your account will remain secure.

                About ADvantage:  
                ADvantage is an AI-powered ad generation platform that helps businesses create 
                engaging and personalized advertisements using the latest trends and data.  

                If you have any questions, feel free to reach out to our support team.

                Best regards,  
                The ADvantage Team  
                advantage.bluemelon@gmail.com  
            """

        send_mail(
            subject,
            message,
            "advantage.bluemelon@gmail.com",  
            [email],
            fail_silently=False,
        )

    except User.DoesNotExist:
        return redirect("forgot-password")  

    return redirect("forgotpw-otp")


def sign_in_error(request):
    if request.method == 'POST':
        # Access the email and password directly from the POST data
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after login
        else:
            # If authentication fails, show an error message
            messages.error(request, "The email address and password you entered do not match our records. Please try again.")
    
    return render(request, 'user_auth/sign_in_error.html')


def dashboard(request):
    return render(request, "user_auth/dashboard.html")


def mainpage(request):
    if request.method == "POST":
        form = AdRequestForm(request.POST, request.FILES)

        # ── 1. print form errors if any ───────────────────────────
        if not form.is_valid():
            print("DEBUG‑FORM‑ERRORS:", form.errors.as_json())
            return render(request, "user_auth/mainpage.html", {"form": form})
        
        if form.is_valid():
            # 1) Explicitly read the checkbox
            include_tags = bool(request.POST.get("include_hashtags"))

            # 2) Save the ad request
            ad_request = form.save(commit=False)
            ad_request.scope = ad_request.scope or "global"
            ad_request.include_hashtags = include_tags
            ad_request.save()

            # Get the request_id of the saved ad_request
            request_id = ad_request.id

            # 3) Build CLI call
            product     = ad_request.product
            description = ad_request.description
            tone        = ad_request.tone
            tag_flag    = "yes" if include_tags else "no"

            script_path = os.path.join(settings.BASE_DIR, "AD_gen", "ad_generator.py")
            cmd = [sys.executable, script_path, product, description, tone, tag_flag]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()
            print("DEBUG‑CLI‑RET:", result.returncode)
            print("DEBUG‑CLI‑STDOUT:\n", result.stdout)
            print("DEBUG‑CLI‑STDERR:\n", result.stderr)
            ads = [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]

            if result.returncode == 0:
                context = {"form": form, "result": ads, "campaign": ad_request, "request_id": request_id}
            else:
                err     = f"Error ({result.returncode}): {stderr or 'no stderr'}"
                context = {"form": form, "error": err, "campaign": ad_request, "request_id": request_id}

            return render(request, "user_auth/mainpage1.html", context)

        # ───────────────── invalid form: fall through here ─────────────────
        return render(request, "user_auth/mainpage.html", {"form": form})

    # GET (or any non‑POST) → blank form
    form = AdRequestForm()
    return render(request, "user_auth/mainpage.html", {"form": form})

def generate_campaign(request):
    if request.method == "POST":
        form = AdRequestForm(request.POST, request.FILES)

        # ── 1. print form errors if any ───────────────────────────
        if not form.is_valid():
            print("DEBUG‑FORM‑ERRORS:", form.errors.as_json())
            return render(request, "user_auth/mainpage.html", {"form": form})
        if form.is_valid():
            # same explicit pull of the checkbox
            include_tags = bool(request.POST.get("include_hashtags"))
            ad_request = form.save(commit=False)
            ad_request.user = request.user
            ad_request.scope = ad_request.scope or "global"
            ad_request.include_hashtags = bool(request.POST.get("include_hashtags"))
            ad_request.save()

            product     = ad_request.product
            description = ad_request.description
            tone        = ad_request.tone
            tag_flag    = "yes" if include_tags else "no"

            script_path = os.path.join(settings.BASE_DIR, "AD_gen", "ad_generator.py")
            cmd = [
    sys.executable,           # <— the exact venv‐python that’s running manage.py
    script_path,
    product, description, tone, tag_flag,
]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()
            print("DEBUG‑CLI‑RET:", result.returncode)
            print("DEBUG‑CLI‑STDOUT:\n", result.stdout)
            print("DEBUG‑CLI‑STDERR:\n", result.stderr)
            ads = [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]

            if result.returncode == 0:
                ads = [line.strip() for line in stdout.splitlines() if line.strip()]
                return render(request, "user_auth/mainpage1.html",{"form": form, "result": ads, "campaign": ad_request})
            else:
                err = f"Error ({result.returncode}): {stderr or 'no stderr'}"
                return render(request, "user_auth/mainpage1.html",
                  {"form": form, "error": err, "campaign": ad_request})

    return redirect("mainpage")

from django.utils.timezone import now  # Make sure this is imported

def select_ads(request, request_id):
    ad_request = get_object_or_404(AdRequest, id=request_id)

    if request.method == "POST":
        # rebuild the edited ads list
        ads = []
        i = 1
        while f"ad_{i}" in request.POST:
            ads.append(request.POST[f"ad_{i}"].strip())
            i += 1

        try:
            picked = int(request.POST.get("selected", "1"))
            if not (1 <= picked <= len(ads)):
                raise ValueError
        except ValueError:
            messages.error(request, "Please select an ad first.")
            return redirect("mainpage")

        chosen_text = ads[picked - 1]
        ad_request.chosen_ad = chosen_text
        ad_request.save()

        user = ad_request.user or request.user  # fallback to current user if needed

        if request.POST.get("action") == "send":
            subject = f"Your Campaign Update: {ad_request.product}"

            # A) if CSV uploaded
            if ad_request.csv_file:
                total = sent = 0
                with open(ad_request.csv_file.path, newline="", encoding="utf-8") as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        total += 1
                        name  = row.get("name", "").strip() or "Customer"
                        email = row.get("email", "").strip()
                        body  = f"Hello {name},\n\n{chosen_text}"
                        res   = send_email(email, subject, body)

                        SentEmail.objects.create(
                            ad_request    = ad_request,
                            user          = user,  # ✅ store the generator
                            customer      = None,
                            email_address = email,
                            success       = res.get("success", False),
                            error_message = res.get("error", ""),
                            sent_at       = now(),  # ✅ consistent time
                        )
                        if res.get("success"):
                            sent += 1

                messages.success(request, f"Sent {sent}/{total} emails.")
                return redirect("dashboard1")

            # B) otherwise blast to all DB customers
            else:
                total = Customer.objects.exclude(email="").count()
                sent = 0
                for cust in Customer.objects.exclude(email=""):
                    body = f"Hello {cust.name or 'Customer'},\n\n{chosen_text}"
                    res  = send_email(cust.email, subject, body)

                    SentEmail.objects.create(
                        ad_request    = ad_request,
                        user          = ad_request.user,  # ✅ store the generator
                        customer      = cust,
                        email_address = cust.email,
                        success       = res.get("success", False),
                        error_message = res.get("error", ""),
                        sent_at       = now(),  # ✅ consistent time
                    )
                    if res.get("success"):
                        sent += 1

                messages.success(request, f"Sent {sent}/{total} emails.")
                return redirect("dashboard1")

        else:
            messages.success(request, "Ad saved!")
            return redirect("dashboard2")

    return redirect("mainpage")

def admin_login(request):
    if request.method == "POST":
        user = request.POST["username"]
        pw   = request.POST["password"]
        if user == "superuser" and pw == "admin":
            request.session["is_admin"] = True
            return redirect("admin_page")
        else:
            return render(request, "user_auth/admin_login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "user_auth/admin_login.html")


def admin_page(request):
    if not request.session.get("is_admin"):
        return redirect("admin_login")

    if request.method == "POST":
        scrape_daily_trends_7d()
        messages.success(request, "7-day trends data updated successfully!")
        return redirect("admin_page")

    total_users = get_user_model().objects.count()

    sent_ads = AdRequest.objects.filter(chosen_ad__isnull=False)

    tone_breakdown = (
        sent_ads.values("tone")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    product_breakdown = (
        sent_ads.values("product")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    user_stats = (
        sent_ads.values("user__first_name", "user__last_name")
        .annotate(sent_ads=Count("id"))
        .order_by("-sent_ads")
    )

    # ✅ FIXED: Add this block properly
    email_logs = (
        SentEmail.objects
        .select_related("ad_request", "ad_request__user")
        .order_by("-sent_at")[:10]
    )

    return render(request, "user_auth/admin_page.html", {
        "total_users": total_users,
        "tone_breakdown": tone_breakdown,
        "product_breakdown": product_breakdown,
        "user_stats": user_stats,
        "email_logs": email_logs,  # ✅ Make sure this gets passed
    })





def dashboard1(request):
    return render(request, 'user_auth/dashboard1.html')  # Ensure you have this template file in your templates folder

def dashboard2(request):
    return render(request, 'user_auth/dashboard2.html')  # Ensure you have this template file in your templates folder

def homepage(request):
    return render(request, "user_auth/homepage.html")

def pricing(request):
    return render(request, "user_auth/pricing.html")

def account_settings(request):
    user = request.user
    return render(request, "user_auth/account.html", {"user": user})
