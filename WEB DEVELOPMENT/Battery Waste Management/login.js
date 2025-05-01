document.addEventListener('DOMContentLoaded', () => {
    const loginBox = document.querySelector('.logreg-box');
    const loginLink = document.querySelector('.login-link');
    const registerLink = document.querySelector('.register-link');
  
    registerLink.addEventListener('click', () => {
      loginBox.setAttribute('class', 'logreg-box active');
    });
  
    loginLink.addEventListener('click', () => {
      loginBox.setAttribute('class', 'logreg-box');
    });
  });
  