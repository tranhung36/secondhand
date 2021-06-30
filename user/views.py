from django.shortcuts import get_object_or_404, render, redirect
from core.models import Item, Category, SubCategory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView
from .models import Profile, User
from .forms import ProfileUpdateForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.


class UserPostItemView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'profile.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cat"] = Category.objects.all()
        context["item_owner"] = get_object_or_404(
            get_user_model(), username=self.kwargs['username'])
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Item.objects.filter(author=user)[:6]


@login_required
def update_profile(request, username):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)

        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('user:profile', username=username)

    else:
        p_form = ProfileUpdateForm(instance=request.user)

    context = {
        'p_form': p_form
    }
    return render(request, 'settings.html', context)
