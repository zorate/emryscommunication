/**
 * Emry Global Tech Realm — Frontend Interaction Logic
 */

document.addEventListener("DOMContentLoaded", () => {

    // ---- Hamburger / Mobile Nav Toggle ----
    const hamburger = document.getElementById("hamburger-btn");
    const drawer    = document.getElementById("nav-drawer");

    if (hamburger && drawer) {
        hamburger.addEventListener("click", () => {
            hamburger.classList.toggle("open");
            drawer.classList.toggle("open");
        });
    }

    // Close nav when clicking outside
    document.addEventListener("click", (e) => {
        if (drawer && drawer.classList.contains("open")) {
            if (!drawer.contains(e.target) && !hamburger.contains(e.target)) {
                drawer.classList.remove("open");
                hamburger.classList.remove("open");
            }
        }
    });

    // ---- Sticky Nav Shrink on Scroll ----
    const nav = document.getElementById("main-nav");
    window.addEventListener("scroll", () => {
        if (nav) {
            nav.style.background = window.scrollY > 60
                ? "rgba(6, 10, 24, 0.97)"
                : "rgba(6, 10, 24, 0.88)";
        }
    });

    // ---- Appointment Booking Form ----
    const appointmentForm = document.getElementById("appointment-form");
    if (appointmentForm) {
        appointmentForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = document.getElementById("appt-submit-btn");
            if (btn) { btn.textContent = "⏳ Submitting..."; btn.disabled = true; }
            const formData = new FormData(appointmentForm);
            try {
                const response = await fetch(appointmentForm.action, {
                    method: "POST",
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    showToast("✅ " + result.message, "success");
                    appointmentForm.reset();
                } else {
                    showToast("❌ " + result.message, "error");
                }
            } catch (err) {
                showToast("❌ Network error. Please try again.", "error");
            } finally {
                if (btn) { btn.textContent = "📅 Submit Booking"; btn.disabled = false; }
            }
        });
    }

    // ---- Legacy Apprentice Form (if present) ----
    const apprenticeForm = document.getElementById("apprentice-form");
    if (apprenticeForm) {
        apprenticeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(apprenticeForm);
            try {
                const response = await fetch(apprenticeForm.action, { method: "POST", body: formData });
                const result = await response.json();
                if (result.success) {
                    showToast(result.message, "success");
                    apprenticeForm.reset();
                    toggleGuardianPhone(false);
                } else {
                    showToast(result.message, "error");
                }
            } catch (err) {
                showToast("Network error. Please try again.", "error");
            }
        });
    }

    // ---- Admin Login Form ----
    const loginForm = document.getElementById("admin-login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            try {
                const response = await fetch(window.location.href, { method: "POST", body: formData });
                const result = await response.json();
                if (result.success) {
                    showToast("✅ Access granted. Loading dashboard...", "success");
                    setTimeout(() => { window.location.reload(); }, 1000);
                } else {
                    showToast("❌ " + result.message, "error");
                }
            } catch (err) {
                showToast("❌ Authentication error.", "error");
            }
        });
    }

    // ---- Admin Media Upload Form ----
    const mediaForm = document.getElementById("media-upload-form");
    if (mediaForm) {
        mediaForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(mediaForm);
            try {
                const response = await fetch("/admin/upload_media", { method: "POST", body: formData });
                const result = await response.json();
                if (result.success) {
                    showToast("✅ " + result.message, "success");
                    setTimeout(() => { window.location.reload(); }, 1000);
                } else {
                    showToast("❌ " + result.message, "error");
                }
            } catch (err) {
                showToast("❌ Upload failed. Please try again.", "error");
            }
        });
    }

    // ---- Shop Filter Buttons ----
    const filterBtns = document.querySelectorAll(".filter-btn");
    const productCards = document.querySelectorAll(".product-card");

    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            filterBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const filter = btn.dataset.filter;
            productCards.forEach(card => {
                if (filter === "all" || card.dataset.category === filter) {
                    card.classList.remove("hidden");
                } else {
                    card.classList.add("hidden");
                }
            });
        });
    });

    // ---- Scroll-triggered fade-in for section cards ----
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll(".service-card, .media-card, .product-card, .form-card").forEach(el => {
        el.style.opacity = "0";
        el.style.transform = "translateY(20px)";
        el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
        observer.observe(el);
    });
});

/**
 * Close the mobile nav drawer (called from nav links)
 */
function closeNav() {
    const drawer   = document.getElementById("nav-drawer");
    const hamburger = document.getElementById("hamburger-btn");
    if (drawer) drawer.classList.remove("open");
    if (hamburger) hamburger.classList.remove("open");
}

/**
 * Pre-fill appointment service field from shop enquiry button
 */
function prefillAppointment(productName) {
    const serviceSelect = document.getElementById("appt-service");
    const messageField  = document.getElementById("appt-message");
    if (serviceSelect) {
        serviceSelect.value = "Phone Purchase";
    }
    if (messageField && productName) {
        messageField.value = `I am interested in: ${productName}`;
    }
}

/**
 * Toggle guardian phone field visibility (legacy form)
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
 * Admin application status update
 */
async function processApplication(appId, action) {
    try {
        const response = await fetch(`/admin/action/${appId}/${action}`, { method: "POST" });
        const result = await response.json();
        if (result.success) {
            showToast("✅ " + result.message, "success");
            const row = document.getElementById(`row-${appId}`);
            if (row) {
                const badge = row.querySelector(".status-badge");
                badge.textContent = action === "approve" ? "Approved" : "Rejected";
                badge.className = `status-badge ${action === "approve" ? "approved" : "rejected"}`;
            }
        } else {
            showToast("❌ " + result.message, "error");
        }
    } catch (err) {
        showToast("❌ Error processing request.", "error");
    }
}

/**
 * Premium toast notification system
 */
function showToast(message, type = "success") {
    const toast = document.getElementById("toast-notification");
    if (toast) {
        toast.textContent = message;
        toast.style.borderColor = type === "success" ? "#22c55e" : "#ef4444";
        toast.classList.remove("hidden");
        setTimeout(() => { toast.classList.add("hidden"); }, 4500);
    }
}