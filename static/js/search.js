function submitSearchWithAnchor(form) {
    const params = new URLSearchParams(new FormData(form)).toString();
    window.location.href = `${form.action}?${params}#moviesList`;
    return false; // prevent default submit
}

// Optional auto-scroll on page load if URL has hash
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.hash === "#moviesList") {
        const el = document.getElementById("moviesList");
        if (el) el.scrollIntoView({ behavior: "smooth" });
    }
});