/**
 * MyVetPet - Funciones para mostrar/ocultar contraseñas
 * Archivo reutilizable para todos los formularios
 */

/**
 * Función para mostrar/ocultar contraseña en el login
 */
function togglePassword() {
    const passwordField = document.getElementById("password-field");
    const toggleIcon = document.getElementById("toggle-icon");
    togglePasswordField(passwordField, toggleIcon);
}

/**
 * Función para mostrar/ocultar contraseñas en el registro
 */
function togglePasswordRegister() {
    const passwordField1 = document.getElementById("password-field1");
    const passwordField2 = document.getElementById("password-field2");
    const toggleIcon1 = document.getElementById("toggle-icon1");
    const toggleIcon2 = document.getElementById("toggle-icon2");
    
    togglePasswordField(passwordField1, toggleIcon1);
    togglePasswordField(passwordField2, toggleIcon2);
}

/**
 * Función para mostrar/ocultar contraseñas en el reset de password
 */
function togglePasswordReset() {
    const passwordField1 = document.getElementById("new-password1");
    const passwordField2 = document.getElementById("new-password2");
    const toggleIcon1 = document.getElementById("toggle-icon1");
    const toggleIcon2 = document.getElementById("toggle-icon2");
    
    togglePasswordField(passwordField1, toggleIcon1);
    togglePasswordField(passwordField2, toggleIcon2);
}

/**
 * Función genérica para mostrar/ocultar cualquier campo de contraseña
 */
function togglePasswordField(passwordField, toggleIcon) {
    if (passwordField && toggleIcon) {
        if (passwordField.type === "password") {
            // Mostrar contraseña
            passwordField.type = "text";
            toggleIcon.classList.remove("fa-eye");
            toggleIcon.classList.add("fa-eye-slash");
            toggleIcon.title = "Ocultar contraseña";
        } else {
            // Ocultar contraseña
            passwordField.type = "password";
            toggleIcon.classList.remove("fa-eye-slash");
            toggleIcon.classList.add("fa-eye");
            toggleIcon.title = "Mostrar contraseña";
        }
    }
}

/**
 * Mejoras de UX para formularios
 */
document.addEventListener('DOMContentLoaded', function() {
    // Enter en usuario lleva al campo de contraseña (login)
    const usernameField = document.querySelector('input[name="username"]');
    const passwordField = document.getElementById("password-field");
    
    if (usernameField && passwordField) {
        usernameField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                passwordField.focus();
            }
        });
    }
    
    // Enter en contraseña simula click en el botón de login
    if (passwordField) {
        passwordField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const form = this.closest('form');
                if (form) {
                    const submitButton = form.querySelector('button[type="submit"]');
                    if (submitButton) {
                        submitButton.click();
                    }
                }
            }
        });
    }
    
    // Tecla Escape para ocultar contraseña si está visible
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const allPasswordFields = document.querySelectorAll('input[type="text"][id*="password"]');
            allPasswordFields.forEach(field => {
                field.type = "password";
                const iconId = field.id.replace("password", "toggle-icon");
                const icon = document.getElementById(iconId);
                if (icon) {
                    icon.classList.remove("fa-eye-slash");
                    icon.classList.add("fa-eye");
                }
            });
        }
    });
});