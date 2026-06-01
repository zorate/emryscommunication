/**
 * Emrys Communications Core Frontend Interaction Architecture Blueprint
 */

document.addEventListener("DOMContentLoaded", () => {
    // Intercept and handle potential Academy Registration Pipeline Operations
    const apprenticeForm = document.getElementById("apprentice-form");
    if (apprenticeForm) {
        apprenticeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(apprenticeForm);
            
            try {
                const response = await fetch(apprenticeForm.action, {
                    method: "POST",
                    body: formData
                });
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message, "success");
                    apprenticeForm.reset();
                    toggleGuardianPhone(false); // Ensure hidden state restored
                } else {
                    showToast(result.message, "error");
                }
            } catch (err) {
                showToast("Network matrix latency pipeline drop failure context.", "error");
            }
        });
    }

    // Intercept Administrative Secure Login Interception Modules
    const loginForm = document.getElementById("admin-login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            
            try {
                const response = await fetch(window.location.href, {
                    method: "POST",
                    body: formData
                });
                const result = await response.json();
                
                if (result.success) {
                    showToast("Authentication confirmed. Accessing matrix layer...", "success");
                    setTimeout(() => { window.location.reload(); }, 1000);
                } else {
                    showToast(result.message, "error");
                }
            } catch (err) {
                showToast("Critical operational validation logic anomaly discovered.", "error");
            }
        });
    }

    // Intercept Administrative GridFS Broadcasting Submissions Interface
    const mediaForm = document.getElementById("media-upload-form");
    if (mediaForm) {
        mediaForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(mediaForm);
            
            try {
                const response = await fetch("/admin/upload_media", {
                    method: "POST",
                    body: formData
                });
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message, "success");
                    setTimeout(() => { window.location.reload(); }, 1000);
                } else {
                    showToast(result.message, "error");
                }
            } catch (err) {
                showToast("GridFS transaction delivery path failure.", "error");
            }
        });
    }
});

/**
 * Handle Multi-Step Guardian Optional Toggle Fields Visibility Context
 */
function toggleGuardianPhone(showCustom) {
    const customPhoneField = document.getElementById("guardian_phone");
    if (customPhoneField) {
        if (showCustom) {
            customPhoneField.style.display = "block";
            customPhoneField.setAttribute("required", "required");
        } else {
            customPhoneField.style.display = "none";
            customPhoneField.removeAttribute("required");
        }
    }
}

/**
 * Administrative Applicant Process Management Pipelines Status Updates Action Tools
 */
async function processApplication(appId, action) {
    try {
        const response = await fetch(`/admin/action/${appId}/${action}`, { method: "POST" });
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, "success");
            // Dynamic modern targeted inline DOM transformation updates instantly without hard structural browser reloading cycles
            const row = document.getElementById(`row-${appId}`);
            if (row) {
                const statusBadge = row.querySelector(".status-badge");
                statusBadge.textContent = action === "approve" ? "Approved" : "Rejected";
                statusBadge.className = `status-badge ${action === "approve" ? "approved" : "rejected"}`;
            }
        } else {
            showToast(result.message, "error");
        }
    } catch (err) {
        showToast("Error processing data modification directive matrix rules.", "error");
    }
}

/**
 * Custom Glassmorphic System Notification Toast Controller Function Node
 */
function showToast(message, type = "success") {
    const toast = document.getElementById("toast-notification");
    if (toast) {
        toast.textContent = message;
        toast.style.borderColor = type === "success" ? "#00ff95" : "#ff0062";
        toast.classList.remove("hidden");
        
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 4000);
    }
}