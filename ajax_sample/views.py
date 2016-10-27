from ozp.decorators.cas_decorators import redirecting_login_required
from django.http import HttpResponse
from django.template import loader
from random import randint


def base_view(request):
    template = loader.get_template('ajax_sample_base.html')
    return HttpResponse(template.render(request=request))


@redirecting_login_required
def status_view(request):
    return HttpResponse(randint(1, 20))


