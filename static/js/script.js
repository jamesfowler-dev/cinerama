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

// Ensure bookingSeatSelector exists at global scope ASAP so templates/console can reference it
// without depending on DOMContentLoaded ordering. If it was already defined later, this
// will not overwrite it.
(function(){
    if(window.bookingSeatSelector) return;

    window.bookingSeatSelector = (function(){
        function init(containerSelector, opts) {
            opts = opts || {};
            var container = (typeof containerSelector === 'string') ? document.querySelector(containerSelector) : containerSelector;
            console.debug && console.debug('bookingSeatSelector.init called for', containerSelector, container, opts);
            if(!container) return null;

            var isModal = !!opts.modal;

            // If this container was already initialized, return the existing instance to avoid
            // double-binding event handlers (templates or auto-init may call init multiple times).
            try {
                var existing = container.__bookingSeatSelector;
                if (existing) {
                    // If an existing instance is present, allow updating it with new options
                    try { if (typeof existing._update === 'function') existing._update(opts); } catch(e) {}
                    return existing;
                }
            } catch (e) { /* ignore */ }

            var selectedListEl = container.querySelector('#modalSelectedSeatsList') || document.getElementById('selectedSeatsList') || document.getElementById('selectedSeatsDisplay');
            var quantityEl = container.querySelector('#modalSeatQuantity') || document.getElementById('seatQuantity');
            var totalEl = container.querySelector('#modalTotalPrice') || document.getElementById('totalPrice');
            var selectedSeatsInputEl = document.getElementById('selectedSeatsInput');
            var proceedBtn = container.querySelector('#modalConfirmSeats') || document.getElementById('proceedBtn');
            var bookingForm = document.getElementById('bookingForm');

            var seatPrice = parseFloat(container.dataset.showtimePrice || opts.showtimePrice || 0) || 0;
            var showtimeId = parseInt(container.dataset.showtimeId || opts.showtimeId || 0) || 0;
            var bookingId = container.dataset.bookingId || opts.bookingId || null;

            var seats = container.querySelectorAll('.seat.available');
            var selectedSeats = [];

            function updateSummary(){
                try {
                    if(selectedListEl){
                        if(selectedListEl.tagName.toLowerCase() === 'div'){
                            selectedListEl.innerHTML = selectedSeats.length === 0 ? '<span class="text-muted">None selected</span>' : selectedSeats.map(function(s){ return s.number; }).join(', ');
                        } else {
                            selectedListEl.innerHTML = selectedSeats.length === 0 ? '<li class="text-muted">No seats selected</li>' : selectedSeats.map(function(seat){
                                return '<li class="d-flex justify-content-between"><span>Seat '+seat.number+'</span><span>£'+seatPrice+'</span></li>';
                            }).join('');
                        }
                    }

                    if(quantityEl) quantityEl.textContent = selectedSeats.length;
                    if(totalEl) totalEl.textContent = '£' + (selectedSeats.length * seatPrice).toFixed(2);

                    if(selectedSeatsInputEl){
                        selectedSeatsInputEl.innerHTML = selectedSeats.map(function(seat){
                            return '<input type="hidden" name="selected_seats" value="'+seat.id+'">';
                        }).join('');
                    }

                    if(proceedBtn) proceedBtn.disabled = selectedSeats.length === 0;
                } catch(e){ console.warn('updateSummary error', e); }
            }

            function toggleSeat(btn){
                var id = btn.getAttribute('data-seat-id');
                var number = btn.getAttribute('data-seat-number');
                if(btn.classList.contains('selected')){
                    btn.classList.remove('selected');
                    selectedSeats = selectedSeats.filter(function(s){ return s.id !== id; });
                } else {
                    if(selectedSeats.length >= (opts.maxSeats || 8)) { alert('Max '+(opts.maxSeats||8)+' seats'); return; }
                    btn.classList.add('selected');
                    selectedSeats.push({id: id, number: number});
                }
                updateSummary();
            }

            seats.forEach(function(btn){ btn.addEventListener('click', function(){ toggleSeat(btn); }); });

            if(bookingForm){
                bookingForm.addEventListener('submit', function(e){
                    if(selectedSeats.length === 0){ e.preventDefault(); alert('Please select at least one seat.'); }
                });
            }

            if(isModal && proceedBtn){
                proceedBtn.addEventListener('click', function(){
                    if(selectedSeats.length === 0){ alert('Please select at least one seat.'); return; }
                    if(!bookingId){ alert('Missing booking id'); return; }
                    var url = '/booking/confirm-reselect/' + bookingId + '/';
                    var csrftokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
                    var csrftoken = csrftokenEl ? csrftokenEl.value : '';
                    var formData = new FormData();
                    formData.append('showtime_id', showtimeId);
                    selectedSeats.forEach(function(s){ formData.append('selected_seats', s.id); });
                    fetch(url, { method: 'POST', body: formData, headers: {'X-CSRFToken': csrftoken}, credentials: 'same-origin' })
                        .then(function(r){ if(r.redirected) window.location = r.url; else return r.json(); })
                        .then(function(data){ if(data && data.error) alert(data.error); })
                        .catch(function(err){ console.error(err); alert('An error occurred'); });
                });
            }

            updateSummary();

            var instance = {
                getSelectedSeats: function(){ return selectedSeats.slice(); },
                _update: function(newOpts){
                    try {
                        newOpts = newOpts || {};
                        if(newOpts.showtimePrice !== undefined && newOpts.showtimePrice !== null){
                            seatPrice = parseFloat(newOpts.showtimePrice) || seatPrice;
                        }
                        if(newOpts.showtimeId !== undefined && newOpts.showtimeId !== null){
                            showtimeId = parseInt(newOpts.showtimeId) || showtimeId;
                        }
                        if(newOpts.bookingId !== undefined && newOpts.bookingId !== null){
                            bookingId = newOpts.bookingId;
                        }
                        // re-run summary to reflect updated price
                        updateSummary();
                    } catch(e){ console.warn('bookingSeatSelector._update error', e); }
                }
            };
            try { container.__bookingSeatSelector = instance; } catch(e) { /* ignore */ }
            return instance;
        }

        return { init: init };
    })();

})();

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
    // bookingSeatSelector is defined globally above; no need to redefine here.


});

// Auto-init: if a seat map exists on the page, initialize bookingSeatSelector after DOM ready.
document.addEventListener('DOMContentLoaded', function(){
    try {
        var map = document.getElementById('seatMap');
        if(map && window.bookingSeatSelector && typeof window.bookingSeatSelector.init === 'function'){
            var price = parseFloat(map.dataset.showtimePrice || map.getAttribute('data-showtime-price') || 0) || 0;
            var showtimeId = parseInt(map.dataset.showtimeId || map.getAttribute('data-showtime-id') || 0) || 0;
            window.bookingSeatSelector.init('#seatMap', { modal: false, showtimePrice: price, showtimeId: showtimeId });
        }
    } catch(e) { /* ignore */ }
});
