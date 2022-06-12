import time
from dataclasses import dataclass

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_control
from faker import Faker

from example.core.forms import OddNumberForm


@require_http_methods(("GET",))
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


# CSRF Demo


@require_http_methods(("GET",))
@cache_control(max_age=3600)
def csrf_demo(request: HttpRequest) -> HttpResponse:
    return render(request, "csrf-demo.html")


@require_http_methods(("POST",))
def csrf_demo_checker(request: HttpRequest) -> HttpResponse:
    form = OddNumberForm(request.POST)
    if form.is_valid():
        number = form.cleaned_data["number"]
        number_is_odd = number % 2 == 1
    else:
        number_is_odd = False
    return render(
        request,
        "csrf-demo-checker.html",
        {"form": form, "number_is_odd": number_is_odd},
    )


# Error demo


@require_http_methods(("GET",))
@cache_control(max_age=3600)
def error_demo(request: HttpRequest) -> HttpResponse:
    return render(request, "error-demo.html", { "title": "Error Demo"})


@require_http_methods(("GET",))
def error_demo_trigger(request: HttpRequest) -> HttpResponse:
    1 / 0
    return render(request, "error-demo.html")  # unreachable


# Middleware tester

# This uses two views - one to render the form, and the second to render the
# table of attributes.


@require_http_methods(("GET",))
def middleware_tester(request: HttpRequest) -> HttpResponse:
    return render(request, "middleware-tester.html")


@require_http_methods(["DELETE", "POST", "PUT"])
def middleware_tester_table(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "middleware-tester-table.html",
        {"timestamp": time.time()},
    )


# Partial rendering example


# This dataclass acts as a stand-in for a database model - the example app
# avoids having a database for simplicity.


@dataclass
class Person:
    id: int
    name: str


faker = Faker()
people = [Person(id=i, name=faker.name()) for i in range(1, 235)]


@require_http_methods(("GET",))
def partial_rendering(request: HttpRequest) -> HttpResponse:
    # Standard Django pagination
    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=people, per_page=10).get_page(page_num)

    # The htmx magic - use a different, minimal base template for htmx
    # requests, allowing us to skip rendering the unchanging parts of the
    # template.
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "_base.html"

    return render(
        request,
        "partial-rendering.html",
        {
            "base_template": base_template,
            "page": page,
        },
    )


from django.views.generic import FormView


from django import forms
from django.core.exceptions import ValidationError

class SignupForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    email = forms.EmailField(label='Your email', max_length=100)
    repeat_email = forms.EmailField(label='Repeat your email', max_length=100)

    def clean_repeat_email(self):
        if self.cleaned_data.get('email') != self.cleaned_data.get('repeat_email'):
            raise ValidationError("Emails must match!")
        return self.cleaned_data['repeat_email']


from django.urls import reverse_lazy

class SignUpView(FormView):
    form_class: forms.Form = SignupForm
    template_name: str = 'form-demo.html'
    success_url = reverse_lazy('form-demo')

    def form_valid(self, form):
        if self.request.htmx:
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)
