from django.shortcuts import render, redirect ,get_object_or_404
from .models import Movie,Theater,Seat,Booking
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

def movie_list(request):
    search_query=request.GET.get('search')
    if search_query:
        movies=Movie.objects.filter(name__icontains=search_query)
    else:
        movies=Movie.objects.all()
    return render(request,'movies/movie_list.html',{'movies':movies})

"""

def theater_list(request,movie_id):
    movie = get_object_or_404(Movie,id=movie_id)
    theater=Theater.objects.filter(movie=movie)
    return render(request,'movies/theater_list.html',{'movie':movie,'theaters':theater}) 
"""

# in movie/views.py

def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    # We don't need to do anything special here because we can use the model methods directly in the template
    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theaters': theaters
    })


@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theaters = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theaters).order_by('seat_number')

    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('seats')
        error_seats = []

        if not selected_seat_ids:
            return render(request, "movies/seat_selection.html", {
                'theaters': theaters,
                "seats": seats,
                'error': "⚠️ Please select at least one seat before booking."
            })

        for seat_id in selected_seat_ids:
            seat = get_object_or_404(Seat, id=seat_id, theater=theaters)
            if seat.is_booked:
                error_seats.append(seat.seat_number)
            else:
                try:
                    Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theaters.movie,
                        theater=theaters
                    )
                    seat.is_booked = True
                    seat.save()
                except IntegrityError:
                    error_seats.append(seat.seat_number)

        if error_seats:
            error_message = f"⚠️ These seats are already booked: {', '.join(error_seats)}"
            return render(request, 'movies/seat_selection.html', {
                'theaters': theaters,
                "seats": seats,
                'error': error_message
            })

        # ✅ All seats booked successfully
        return redirect('profile')
    


    return render(request, 'movies/seat_selection.html', {
        'theaters': theaters,
        "seats": seats
    })

