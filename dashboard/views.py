from django.shortcuts import render

def dashboard_view(request):
    # Sample data - replace with actual database queries later
    context = {
        'new_releases': [
            {'title': 'Latest Movie 1', 'poster': 'images/movie1.jpg'},
            {'title': 'Latest Movie 2', 'poster': 'images/movie2.jpg'},
            {'title': 'Latest Movie 3', 'poster': 'images/movie3.jpg'},
        ],
        'classic_films': [
            {'title': 'Classic Film 1', 'poster': 'images/classic1.jpg'},
            {'title': 'Classic Film 2', 'poster': 'images/classic2.jpg'},
            {'title': 'Classic Film 3', 'poster': 'images/classic3.jpg'},
        ],
        'whats_on': [
            {
                'title': 'Movie Title 1',
                'poster': 'images/movie1.jpg',
                'showtimes': ['14:00', '17:30', '20:00', '22:30'],
                'rating': 'PG-13',
                'genre': 'Action, Adventure'
            },
            {
                'title': 'Movie Title 2',
                'poster': 'images/movie2.jpg',
                'showtimes': ['15:00', '18:00', '21:00'],
                'rating': '15',
                'genre': 'Drama, Thriller'
            },
            {
                'title': 'Movie Title 3',
                'poster': 'images/movie3.jpg',
                'showtimes': ['16:00', '19:00', '21:45'],
                'rating': 'PG',
                'genre': 'Comedy, Family'
            },
        ]
    }
    return render(request, 'dashboard/dashboard.html', context)
