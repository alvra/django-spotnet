from django.utils.translation import ugettext as _
try:
    from django.shortcuts import render
except ImportError:
    # for django==1.2 compatibility
    from django.shortcuts import render_to_response
    from django.template import RequestContext
    def render(request, template, context):
        return render_to_response(
            template,
            context,
            context_instance=RequestContext(request),
        )


def index(request):
    return render(
        request,
        'index.html', 
        {},
    )
