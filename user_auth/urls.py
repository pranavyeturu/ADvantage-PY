from django.urls import path
from .views import signup, login_view, password_reset, forgot_password, update_pw_error, dashboard, forgotpw_otp, sign_in_error, resend_otp, forgotpw_emailerror, otp_error, mainpage, generate_campaign, select_ads, admin_login, admin_page, homepage, pricing, account_settings, dashboard1, dashboard2


urlpatterns = [
    path("", homepage, name="homepage"),
    path("account/", account_settings, name="account"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("reset-password/", password_reset, name="reset-password"),
    path("forgot-password/", forgot_password, name="forgot-password"),
    path("forgot-password/error/", forgotpw_emailerror, name="forgotpw-email-error"),
    path("forgotpw-otp/", forgotpw_otp, name="forgotpw-otp"),  
    path("resend_otp/", resend_otp, name="resend-otp"),
    path("update-password-error/", update_pw_error, name="update-pw-error"),
    path("dashboard/", dashboard, name="dashboard"),
    path('sign-in-error/', sign_in_error, name='sign_in_error'),
    path("otp-error/", otp_error, name="otp-error"),
    path('mainpage/', mainpage, name='mainpage'),
    path('generate_campaign/', generate_campaign, name='generate_campaign'),
    path('ads/<int:request_id>/select/', select_ads, name='select_ads'),
    path("admin-login/", admin_login, name="admin_login"),
    path("admin-dashboard/", admin_page, name="admin_page"),
    path("history/", pricing, name="pricing"),
    path('dashboard1/', dashboard1, name='dashboard1'),
    path('dashboard2/', dashboard2, name='dashboard2'),
]