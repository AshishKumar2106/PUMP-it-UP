function validateForm() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const errorMessage = document.getElementById('error-message');

    errorMessage.textContent = '';

    if (username.length < 3) {
        errorMessage.textContent = 'Username must be at least 3 characters long!';
        return false;
    }

    if (!email.includes('@') || !email.includes('.')) {
        errorMessage.textContent = 'Please enter a valid email address!';
        return false;
    }

    if (password.length < 6) {
        errorMessage.textContent = 'Password must be at least 6 characters long!';
        return false;
    }

    if (password !== confirmPassword) {
        errorMessage.textContent = 'Passwords do not match!';
        return false;
    }

    return true;
}

function validateCalcForm() {
    const weight = document.getElementById('weight').value;
    const height = document.getElementById('height').value;
    const heightCm = document.getElementById('height_cm').value;
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value.toLowerCase();
    const errorMessage = document.getElementById('calc-error');

    errorMessage.textContent = '';

    if (weight <= 0 || height <= 0 || heightCm <= 0 || age <= 0) {
        errorMessage.textContent = 'Values must be positive!';
        return false;
    }

    if (gender !== 'male' && gender !== 'female') {
        errorMessage.textContent = 'Gender must be "male" or "female"!';
        return false;
    }

    return true;
}

function openTab(tabName) {
    const tabs = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].style.display = 'none';
    }
    document.getElementById(tabName).style.display = 'block';

    const buttons = document.getElementsByClassName('tab-button');
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('active');
    }
    event.currentTarget.classList.add('active');
}

document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('dark-mode-toggle');
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            toggleButton.textContent = isDark ? 'Light Mode' : 'Dark Mode';
            // Update content background and text color
            const content = document.querySelector('.content');
            if (content) {
                content.style.backgroundColor = isDark ? 'rgba(0, 0, 0, 0.9)' : 'transparent';
                content.style.color = isDark ? '#fff' : '#fff'; // Ensure text stays readable
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('input', validateForm);
    }

    const calcForm = document.getElementById('calcForm');
    if (calcForm) {
        calcForm.addEventListener('input', validateCalcForm);
    }

    const tabButtons = document.getElementsByClassName('tab-button');
    if (tabButtons.length > 0) {
        tabButtons[0].click();  // Open first tab by default
    }
});