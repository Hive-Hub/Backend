import logging
from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

logger = logging.getLogger(__name__)


class APIService:
    """
    Service to map and inspect all registered Django endpoints and paths.
    """

    @staticmethod
    def get_all_routes(resolver=None, prefix=''):
        """
        Recursively extract all URL routes and patterns.
        """
        if resolver is None:
            resolver = get_resolver()
        
        routes = []
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLResolver):
                routes.extend(APIService.get_all_routes(pattern, prefix + str(pattern.pattern)))
            elif isinstance(pattern, URLPattern):
                routes.append({
                    "pattern": prefix + str(pattern.pattern),
                    "name": pattern.name,
                    "callback": str(pattern.callback)
                })
        return routes
