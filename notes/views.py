from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .models import Note, Comment, Category, Tag, Notification
from .forms import NoteForm, CommentForm, CustomUserCreationForm, UserProfileForm, SearchForm
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User

def home(request):
    public_notes = Note.objects.filter(is_public=True).order_by('-created_at')[:5]
    return render(request, 'notes/home.html', {'public_notes': public_notes})

@login_required
def dashboard(request):
    user_notes = Note.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'notes/dashboard.html', {'notes': user_notes})

@login_required
def create_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user
            note.save()
            form.save_tags(note)
            return redirect('dashboard')
    else:
        form = NoteForm()
    return render(request, 'notes/create_note.html', {'form': form})

@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES, instance=note)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = NoteForm(instance=note)
    return render(request, 'notes/edit_note.html', {'form': form, 'note': note})

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('dashboard')
    return render(request, 'notes/delete_note.html', {'note': note})

def view_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if not note.is_public and (not request.user.is_authenticated or note.author != request.user):
        return redirect('home')
    
    note.views += 1
    note.save()

    comments = note.comments.all().order_by('-created_at')
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.note = note
            comment.author = request.user
            comment.save()
            return redirect('view_note', note_id=note.id)
    else:
        comment_form = CommentForm()

    return render(request, 'notes/view_note.html', {
        'note': note,
        'comments': comments,
        'comment_form': comment_form
    })

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'notes/register.html', {'form': form})

@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'notes/user_profile.html', {'form': form})

@login_required
def like_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.user in note.likes.all():
        note.likes.remove(request.user)
        liked = False
    else:
        note.likes.add(request.user)
        liked = True
    return JsonResponse({'likes': note.likes.count(), 'liked': liked})

def search_notes(request):
    form = SearchForm(request.GET)
    notes = Note.objects.filter(is_public=True)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        tags = form.cleaned_data.get('tags')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')

        if query:
            notes = notes.filter(Q(title__icontains=query) | Q(content__icontains=query))
        if category:
            notes = notes.filter(category=category)
        if tags:
            notes = notes.filter(tags__in=tags).distinct()
        if date_from:
            notes = notes.filter(created_at__gte=date_from)
        if date_to:
            notes = notes.filter(created_at__lte=date_to)

    paginator = Paginator(notes, 10)  # Show 10 notes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notes/search_results.html', {'form': form, 'page_obj': page_obj})

@login_required
def share_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            note.shared_with.add(user)
            Notification.objects.create(
                user=user,
                content=f"{request.user.username} shared a note with you: {note.title}"
            )
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def notifications(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'notes/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def export_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, author=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{note.title}.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    p.drawString(100, 100, note.title)
    p.drawString(100, 80, note.content)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

