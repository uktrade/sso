from django.views import View
from django.http.response import HttpResponse

import core.mixins


class TestView(core.mixins.NoIndexMixin, View):
    def get(self, *args, **kwargs):
        return HttpResponse()


def test_no_index_mixin(rf):
    request = rf.get('/')
    view = TestView.as_view()
    response = view(request)

    assert response.status_code == 200
    assert response['X-Robots-Tag'] == 'noindex'