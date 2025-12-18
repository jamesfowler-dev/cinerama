// Dashboard functionality

function showFilms(type) {
    const newBtn = document.getElementById('newReleasesBtn');
    const classicBtn = document.getElementById('classicFilmsBtn');
    const newCarousel = document.getElementById('newReleasesCarousel');
    const classicCarousel = document.getElementById('classicFilmsCarousel');

    if (!newCarousel || !classicCarousel) {
        return;
    }

    if (type === 'new') {
        newBtn.classList.add('active');
        classicBtn.classList.remove('active');
        newCarousel.style.display = 'block';
        classicCarousel.style.display = 'none';
    } else if (type === 'classic') {
        classicBtn.classList.add('active');
        newBtn.classList.remove('active');
        classicCarousel.style.display = 'block';
        newCarousel.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const dateButtons = document.querySelectorAll('[data-date]');
    const customDateInput = document.getElementById('customDate');
    const genreFilter = document.getElementById('genreFilter');
    const dateFilter = document.querySelector('.date-filter');
    const resultsAnchor = '#moviesList';
    
    // Get selected values from URL params
    const urlParams = new URLSearchParams(window.location.search);
    const selectedDate = urlParams.get('date') || 'today';
    const selectedGenre = urlParams.get('genre') || '';
    
    // Reset loading state on page load
    const spinner = document.getElementById('loadingSpinner');
    const moviesList = document.getElementById('moviesList');
    if (spinner) spinner.style.display = 'none';
    if (moviesList) moviesList.style.opacity = '1';

    // If arriving with a hash or filters, ensure results are in view
    const moviesListEl = document.getElementById('moviesList');
    if (window.location.hash === resultsAnchor && moviesListEl) {
        moviesListEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else if ((urlParams.has('date') || urlParams.has('genre')) && moviesListEl) {
        moviesListEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Highlight the currently selected date button
    dateButtons.forEach(button => {
        if (button.dataset.date === selectedDate) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }

        button.addEventListener('click', function (e) {
            e.preventDefault();
            showLoadingSpinner();
            
            const params = new URLSearchParams(window.location.search);
            params.set('date', this.dataset.date);
            if (genreFilter && genreFilter.value) {
                params.set('genre', genreFilter.value);
            } else {
                params.delete('genre');
            }
            // Navigate with anchor so the results are in view after reload
            window.location.href = window.location.pathname + '?' + params.toString() + resultsAnchor;
        });
    });

    // Custom date input
    if (customDateInput) {
        customDateInput.value = selectedDate.length === 10 ? selectedDate : '';
        customDateInput.addEventListener('change', function () {
            if (this.value) {
                showLoadingSpinner();
                const params = new URLSearchParams(window.location.search);
                params.set('date', this.value);
                if (genreFilter && genreFilter.value) {
                    params.set('genre', genreFilter.value);
                } else {
                    params.delete('genre');
                }
                window.location.href = window.location.pathname + '?' + params.toString() + resultsAnchor;
            }
        });
    }

    // Genre filter
    if (genreFilter) {
        if (selectedGenre) {
            genreFilter.value = selectedGenre;
        }

        genreFilter.addEventListener('change', function () {
            showLoadingSpinner();
            const params = new URLSearchParams(window.location.search);
            if (this.value) {
                params.set('genre', this.value);
            } else {
                params.delete('genre');
            }
            window.location.href = window.location.pathname + '?' + params.toString() + resultsAnchor;
        });
    }

    // Loading spinner helper
    function showLoadingSpinner() {
        const spinner = document.getElementById('loadingSpinner');
        const moviesList = document.getElementById('moviesList');
        if (spinner && moviesList) {
            moviesList.style.opacity = '0.3';
            spinner.style.display = 'block';
            spinner.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    // Booking redirect
    window.bookTicket = function (showtimeId) {
        window.location.href = `/booking/select-seats/${showtimeId}/`;
    };

    // Update booking summary
    function updateBookingSummary() {
        const selectedSeatsDisplay = document.getElementById('selectedSeatsDisplay');
        
        // Update selected seats display
        if (selectedSeats.length === 0) {
            selectedSeatsDisplay.innerHTML = '<span class="text-muted">None selected</span>';
        } else {
            selectedSeatsDisplay.innerHTML = selectedSeats.map(seat => seat.number).join(', ');
        }

        // Update quantity and total
        seatQuantity.textContent = selectedSeats.length;
        const total = selectedSeats.length * seatPrice;
        totalPrice.textContent = `£${total.toFixed(2)}`;

        // Update form inputs
        selectedSeatsInput.innerHTML = selectedSeats.map(seat => 
            `<input type="hidden" name="selected_seats" value="${seat.id}">`
        ).join('');

        // Enable/disable proceed button
        proceedBtn.disabled = selectedSeats.length === 0;
    }
});
