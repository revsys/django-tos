from tos.compat import url as tos_url, get_library


Library = get_library()
register = Library()


@register.tag
def url(parser, token):
    return tos_url(parser, token)
