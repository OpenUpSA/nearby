from django.conf import settings


def google_analytics(request):
    """
    Add the Google Analytics tracking ID and domain to the context for use when
    rendering tracking code.
    """
    ga_tracking_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', False)
    if ga_tracking_id:
        return {
            'GOOGLE_ANALYTICS_ID': ga_tracking_id,
        }
    return {}
