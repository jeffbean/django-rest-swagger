# coding=utf-8
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.core import exceptions

from rest_framework_swagger import SWAGGER_SETTINGS


class APIDocView(APIView):
    def initial(self, request, *args, **kwargs):
        self.permission_classes = (self.get_permission_class(request),)
        self.renderer_classes = self.get_renderer_classes(request)
        protocol = "https" if request.is_secure() else "http"
        self.host = request.build_absolute_uri()
        self.api_path = SWAGGER_SETTINGS['api_path']
        self.api_full_uri = "%s://%s%s" % (
            protocol, request.get_host(), self.api_path)

        return super(APIDocView, self).initial(request, *args, **kwargs)

    def get_permission_class(self, request):
        if SWAGGER_SETTINGS['is_superuser'] and not request.user.is_superuser:
            return IsAdminUser
        if SWAGGER_SETTINGS['is_authenticated'] and not request.user.is_authenticated():
            return IsAuthenticated

        return AllowAny

    def get_renderer_classes(self, request):
        render_class_list = []
        class_tuple = SWAGGER_SETTINGS.get('renderer_classes', None)
        if not class_tuple:
            render_class_list.append(JSONRenderer)
        for render_class in class_tuple:
            try:
                dot = render_class.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured, '{0:s} isn\'t a ' \
                                                       'renderer module' \
                    .format(render_class)
            render_module, render_classname = render_class[:dot], render_class[
                                                                 (dot + 1):]
            try:
                mod = __import__(render_module, {}, {}, [''])
            except ImportError, e:
                raise exceptions.ImproperlyConfigured, 'Error importing ' \
                                                       'renderer module {' \
                                                       '0:s}: "{' \
                                                       '1:s}"'.format(
                    render_module, e)
            try:
                render_class_list.append(getattr(mod, render_classname))
            except AttributeError:
                raise exceptions.ImproperlyConfigured, 'Renderer module ' \
                                                       '"{0:s}" does not ' \
                                                       'define ' \
                                                       'a "{0:s}" class' \
                    .format(render_module, render_classname)

        return render_class_list



