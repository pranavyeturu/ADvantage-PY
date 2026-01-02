document.addEventListener("DOMContentLoaded", function () {
  // Function to toggle password visibility
  function togglePasswordVisibility(inputElement, toggleElement) {
    if (inputElement && toggleElement) {
      toggleElement.addEventListener("click", function () {
        if (inputElement.type === "password") {
          inputElement.type = "text"; // Show password
        } else {
          inputElement.type = "password"; // Hide password
        }
      });
    }
  }

 const loginPasswordInput = document.getElementById("password");
  const loginPasswordToggle = document.querySelector(".password-toggle-login"); // Updated selector for login
  togglePasswordVisibility(loginPasswordInput, loginPasswordToggle);

  // Sign In Error Page (sign_in_error.html) - Password
  const signInPasswordInput = document.getElementById("password");
  const signInPasswordToggle = document.querySelector(".password-toggle-signin-error"); // Updated selector for sign_in_error
  togglePasswordVisibility(signInPasswordInput, signInPasswordToggle);

  // Reset Password Page (reset_password.html) - New Password
  const resetPasswordInput1 = document.querySelector('input[name="new_password"]');
  const resetPasswordToggle1 = document.querySelectorAll(".visibility-icon")[0]; // Targeting the first visibility icon
  togglePasswordVisibility(resetPasswordInput1, resetPasswordToggle1);

  // Reset Password Page (reset_password.html) - Confirm Password
  const resetPasswordInput2 = document.querySelector('input[name="confirm_password"]');
  const resetPasswordToggle2 = document.querySelectorAll(".visibility-icon")[1]; // Targeting the second visibility icon
  togglePasswordVisibility(resetPasswordInput2, resetPasswordToggle2);

  // Update Password Error Page (update_pw_error.html) - New Password
  const updatePasswordInput1 = document.getElementById("password1");
  const updatePasswordToggle1 = document.querySelectorAll(".visibility-icon")[0]; // First visibility icon
  togglePasswordVisibility(updatePasswordInput1, updatePasswordToggle1);

  // Update Password Error Page (update_pw_error.html) - Confirm Password
  const updatePasswordInput2 = document.getElementById("password2");
  const updatePasswordToggle2 = document.querySelectorAll(".visibility-icon")[1]; // Second visibility icon
  togglePasswordVisibility(updatePasswordInput2, updatePasswordToggle2);
});
