
# Create your views here.
import pandas as pd
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Customer, CustomerUpload
from .forms import CustomerUploadForm

# ---------- helper --------------------------------------------------
def _import_df(df):
    """Create/Update Customer rows from a pandas DataFrame."""
    added, updated = 0, 0
    for _, row in df.iterrows():
        email = str(row.get("email", "")).strip()
        if not email:
            continue
        obj, created = Customer.objects.update_or_create(
            email=email,
            defaults={
                "name":  str(row.get("name", "")),
                "phone": str(row.get("phone number", row.get("phone", ""))),
            },
        )
        if created:
            added += 1
        else:
            updated += 1
    return added, updated

# ---------- main view ----------------------------------------------
def upload_customers(request):
    """
    Upload an Excel (.xlsx) OR CSV file with columns:
    name | phone number | email
    """
    if request.method == "POST":
        form = CustomerUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save()                       # saves the file
            path   = upload.file.path

            # Pick parser based on extension
            if path.endswith(".csv"):
                df = pd.read_csv(path)
            else:                                      # .xls/.xlsx/anything else
                df = pd.read_excel(path)

            added, updated = _import_df(df)
            messages.success(
                request,
                f"Imported {added} new & updated {updated} existing customers."
            )
            return redirect("upload-customers")
    else:
        form = CustomerUploadForm()

    customers = Customer.objects.all().order_by("-id")[:15]  # preview
    return render(request, "manage_cust/upload_customers.html",
                  {"form": form, "customers": customers})
