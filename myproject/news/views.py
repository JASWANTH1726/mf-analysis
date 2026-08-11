from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserPreference
from .forms import RegisterForm, NewsFilterForm
from .news_service import fetch_news, fetch_by_newspaper, fetch_recommendations, AREA_QUERY_MAP, NEWSPAPER_NAME_MAP

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'news/login.html')

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )
        UserPreference.objects.create(user=user)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'news/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    pref, _ = UserPreference.objects.get_or_create(user=request.user)
    form = NewsFilterForm(initial={
        'language': pref.language,
        'edition': pref.edition,
        'area': pref.area,
        'newspaper': pref.newspaper,
        'keywords': pref.keywords,
    })

    articles = []
    recommendations = []
    active_newspaper = NEWSPAPER_NAME_MAP.get(pref.newspaper, '')

    if request.method == 'POST':
        form = NewsFilterForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language'] or pref.language
            area = form.cleaned_data['area'] or pref.area
            newspaper = form.cleaned_data['newspaper'] or pref.newspaper
            from_date = form.cleaned_data['date']
            raw_keywords = form.cleaned_data['keywords']
            keywords = [k.strip() for k in raw_keywords.split(',') if k.strip()]

            if form.cleaned_data.get('save_keywords'):
                pref.language = language
                pref.edition = form.cleaned_data['edition'] or pref.edition
                pref.area = area
                pref.newspaper = newspaper
                pref.keywords = raw_keywords
                pref.save()

            active_newspaper = NEWSPAPER_NAME_MAP.get(newspaper, '')

            if newspaper:
                articles = fetch_by_newspaper(newspaper, area, language, from_date)
                # fallback: if newspaper domain gives no results, use keyword/area search
                if not articles:
                    area_term = AREA_QUERY_MAP.get(area, 'India')
                    query = ' OR '.join(keywords) if keywords else area_term
                    articles = fetch_news(query=query, language=language, from_date=from_date)
            else:
                area_term = AREA_QUERY_MAP.get(area, 'India')
                query = ' OR '.join(keywords) if keywords else area_term
                articles = fetch_news(query=query, language=language, from_date=from_date)
    else:
        area_term = AREA_QUERY_MAP.get(pref.area, 'India')
        saved_keywords = pref.get_keywords_list()
        if pref.newspaper:
            articles = fetch_by_newspaper(pref.newspaper, pref.area, pref.language)
            if not articles:
                query = ' OR '.join(saved_keywords) if saved_keywords else area_term
                articles = fetch_news(query=query, language=pref.language)
        else:
            query = ' OR '.join(saved_keywords) if saved_keywords else area_term
            articles = fetch_news(query=query, language=pref.language)

    saved_keywords = pref.get_keywords_list()
    if saved_keywords:
        recommendations = fetch_recommendations(saved_keywords, pref.area, pref.language)

    return render(request, 'news/dashboard.html', {
        'form': form,
        'articles': articles,
        'recommendations': recommendations,
        'pref': pref,
        'active_newspaper': active_newspaper,
    })
