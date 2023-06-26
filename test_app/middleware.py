from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpRequest
from django.utils.translation import gettext as _
from oauth2_provider.models import AccessToken


class TokenMiddleware(MiddlewareMixin):
    """
    Middleware для проверки токена авторизации в заголовке запроса.
    """
    def process_request(self, request: HttpRequest) -> None or JsonResponse:
        if request.path in [
            '/', '/accounts/login/', '/accounts/logout/', '/register/',
        ]:
            return None
        if 'HTTP_AUTHORIZATION' not in request.META:
            return JsonResponse({'error': 'Token is required.'}, status=401)
        token = request.META.get('HTTP_AUTHORIZATION').split()[1]
        try:
            access_token = AccessToken.objects.select_related('application', 'user').get(token=token)
            if access_token.is_valid():
                request.user = access_token.user
                request.application = access_token.application
            else:
                return JsonResponse({'error': _('Token is invalid.')}, status=401)
        except AccessToken.DoesNotExist:
            return JsonResponse({'error': _('Token is invalid.')}, status=401)

