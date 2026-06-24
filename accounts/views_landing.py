from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = 'landing.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)
