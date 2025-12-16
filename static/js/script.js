<!-- JavaScript -->

// function showFilms(type) {
//     const newBtn = document.getElementById('newReleasesBtn');
//     const classicBtn = document.getElementById('classicFilmsBtn');
//     const newCarousel = document.getElementById('newReleasesCarousel');
//     const classicCarousel = document.getElementById('classicFilmsCarousel');
    
//     if (type === 'new') {
//         newBtn.classList.add('active');
//         classicBtn.classList.remove('active');
//         newCarousel.style.display = 'block';
//         classicCarousel.style.display = 'none';
//     } else {
//         classicBtn.classList.add('active');
//         newBtn.classList.remove('active');
//         classicCarousel.style.display = 'block';
//         newCarousel.style.display = 'none';
//     }
// }

// function bookTicket(movieTitle, time) {
//     // Redirect to booking page with movie and time parameters
//     window.location.href = '/booking/?movie=' + encodeURIComponent(movieTitle) + '&time=' + encodeURIComponent(time);
// }

// // Date filter functionality
// document.addEventListener('DOMContentLoaded', function() {
//     const dateButtons = document.querySelectorAll('[data-date]');
//     dateButtons.forEach(button => {
//         button.addEventListener('click', function() {
//             dateButtons.forEach(btn => btn.classList.remove('active'));
//             this.classList.add('active');
            
//             // Here you would typically filter the movies based on the selected date
//             console.log('Filtering by:', this.dataset.date);
//         });
//     });
    
//     // Genre filter
//     document.getElementById('genreFilter').addEventListener('change', function() {
//         // Filter movies by genre
//         console.log('Filtering by genre:', this.value);
//     });
// });