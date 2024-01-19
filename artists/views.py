# Create your views here.
from django.shortcuts import render, redirect
from .models import Artist

def artist_list(request):
    sort_order = request.GET.get('sort_order', 'name')
    sort_direction = request.GET.get('sort_direction', 'asc')
    if sort_direction == 'desc':
        sort_order = '-' + sort_order
    artists = Artist.objects.all().order_by(sort_order)
    return render(request, 'artists/artist_list.html', {'artists': artists, 'sort_order': sort_order, 'sort_direction': sort_direction})

from .forms import ArtistForm

def artist_create(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('artist_list')
    else:
        form = ArtistForm()
    return render(request, 'artists/artist_form.html', {'form': form})