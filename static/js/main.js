// Get DOM elements
const video = document.getElementById("video");
const canvas = document.getElementById("myCanvas");
const ctx = canvas.getContext('2d');
const urlInput = document.getElementById("url");
const emailInput = document.getElementById("email");
const submitButton = document.getElementById("submit");
const registrationForm = document.querySelector("form");
const captureBtn = document.getElementById("captureBtn");

// Hide URL input
if (urlInput) {
    urlInput.value = "";
    urlInput.hidden = true;
}

// Set email placeholder
if (emailInput) {
    emailInput.setAttribute("placeholder", "Email");
}

// Simple video constraints
const constraints = {
    video: {
        width: 640,
        height: 480
    },
    audio: false
};

// Initialize webcam
async function initWebcam() {
    try {
        console.log("Requesting webcam access...");
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        console.log("Got stream:", stream);
        
        // Attach stream to video element
        video.srcObject = stream;
        
        // Wait for video to be ready
        await video.play();
        
        console.log("Video playing:", video.videoWidth, video.videoHeight);
        
    } catch (err) {
        console.error("Error accessing webcam:", err);
        const message = document.createElement('div');
        message.style.color = 'red';
        message.style.padding = '20px';
        message.textContent = 'Camera error: ' + err.message;
        video.parentNode.insertBefore(message, video);
    }
}

// Start webcam when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log("Page loaded, initializing webcam...");
    initWebcam();
});

// Capture photo and return data URL
function capturePhoto() {
    try {
        // Set canvas size to match video
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        
        // Draw video frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to data URL
        return canvas.toDataURL('image/png');
    } catch (err) {
        console.error("Error capturing photo:", err);
        return null;
    }
}

// Preview capture button handler
if (captureBtn) {
    captureBtn.onclick = function() {
        // Take photo
        const photoData = capturePhoto();
        if (!photoData) {
            alert("Failed to capture photo. Please ensure your camera is working.");
            return;
        }

        // Show preview
        const previewImg = document.createElement('img');
        previewImg.src = photoData;
        previewImg.style.position = 'absolute';
        previewImg.style.top = '0';
        previewImg.style.left = '0';
        previewImg.style.width = '100%';
        previewImg.style.height = '100%';
        previewImg.style.objectFit = 'cover';
        previewImg.style.zIndex = '2';

        // Add retry button
        const retryBtn = document.createElement('button');
        retryBtn.className = 'capture-btn';
        retryBtn.style.zIndex = '3';
        retryBtn.innerHTML = '<i class="fas fa-redo"></i> Retake Photo';
        retryBtn.onclick = function() {
            previewImg.remove();
            retryBtn.remove();
            captureBtn.style.display = 'block';
            urlInput.value = '';
        };

        // Add to container
        const container = video.parentElement;
        container.appendChild(previewImg);
        container.appendChild(retryBtn);
        captureBtn.style.display = 'none';

        // Store photo data
        urlInput.value = photoData;
    };
}

// Handle form submission
if (registrationForm) {
    registrationForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate email
        if (!emailInput.value) {
            alert("Please enter your email address");
            return;
        }
        
        // Validate photo
        if (!urlInput.value) {
            alert("Please capture your photo first");
            return;
        }
        
        // Show loading state
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.value = "Registering...";
        }
        
        // Submit the form using native submit
        try {
            // Create hidden form and submit
            const hiddenForm = document.createElement('form');
            hiddenForm.method = 'POST';
            hiddenForm.action = registrationForm.action;
            
            // Add CSRF token if present
            const csrfToken = document.querySelector('input[name="csrf_token"]');
            if (csrfToken) {
                const tokenInput = document.createElement('input');
                tokenInput.type = 'hidden';
                tokenInput.name = 'csrf_token';
                tokenInput.value = csrfToken.value;
                hiddenForm.appendChild(tokenInput);
            }
            
            // Add email and photo data
            const emailField = document.createElement('input');
            emailField.type = 'hidden';
            emailField.name = 'email';
            emailField.value = emailInput.value;
            hiddenForm.appendChild(emailField);
            
            const urlField = document.createElement('input');
            urlField.type = 'hidden';
            urlField.name = 'url';
            urlField.value = urlInput.value;
            hiddenForm.appendChild(urlField);
            
            document.body.appendChild(hiddenForm);
            hiddenForm.submit();
            document.body.removeChild(hiddenForm);
            
        } catch (err) {
            console.error("Error submitting form:", err);
            alert("Failed to register. Please try again.");
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.value = "Complete Registration";
            }
        }
    });
}

// Handle login form submission
const loginForm = document.querySelector('form:not(.register-form)');
if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate email
        if (!emailInput.value) {
            alert("Please enter your email address");
            return;
        }
        
        // Validate photo
        if (!urlInput.value) {
            alert("Please capture your photo first");
            return;
        }
        
        // Show loading state
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.value = "Logging in...";
        }
        
        // Submit the form
        try {
            // Create hidden form and submit
            const hiddenForm = document.createElement('form');
            hiddenForm.method = 'POST';
            hiddenForm.action = loginForm.action;
            
            // Add CSRF token if present
            const csrfToken = document.querySelector('input[name="csrf_token"]');
            if (csrfToken) {
                const tokenInput = document.createElement('input');
                tokenInput.type = 'hidden';
                tokenInput.name = 'csrf_token';
                tokenInput.value = csrfToken.value;
                hiddenForm.appendChild(tokenInput);
            }
            
            // Add email and photo data
            const emailField = document.createElement('input');
            emailField.type = 'hidden';
            emailField.name = 'email';
            emailField.value = emailInput.value;
            hiddenForm.appendChild(emailField);
            
            const urlField = document.createElement('input');
            urlField.type = 'hidden';
            urlField.name = 'url';
            urlField.value = urlInput.value;
            hiddenForm.appendChild(urlField);
            
            document.body.appendChild(hiddenForm);
            hiddenForm.submit();
            document.body.removeChild(hiddenForm);
            
        } catch (err) {
            console.error("Error submitting form:", err);
            alert("Failed to log in. Please try again.");
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.value = "LOGIN";
            }
        }
    });
}

// Handle login photo capture
function login(e) {
    if (e) e.preventDefault();
    
    const photoData = capturePhoto();
    if (!photoData) {
        alert("Failed to capture photo. Please ensure your camera is working.");
        return false;
    }
    
    if (urlInput) {
        urlInput.value = photoData;
    }
    
    return true;
}

// Attach login handler to submit button
if (submitButton && !registrationForm) {
    submitButton.onclick = login;
}