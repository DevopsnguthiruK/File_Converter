document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        // Basic client-side validation
        if (!username || !password) {
            alert('Please enter both username and password');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Store JWT token with secure flags
                localStorage.setItem('token', data.access_token);
                
                // Redirect to dashboard
                window.location.href = '/dashboard';
            } else {
                // Show specific error message
                const errorMessage = data.error || 'Login failed';
                document.getElementById('error-message')?.remove(); // Remove previous error message
                
                const errorDiv = document.createElement('div');
                errorDiv.id = 'error-message';
                errorDiv.className = 'text-red-500 text-sm mt-2 text-center';
                errorDiv.textContent = errorMessage;
                
                loginForm.insertBefore(errorDiv, loginForm.lastElementChild);
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Network error. Please try again.');
        }
    });
});