from web.resolvUrl import ResolvUrl
from web.webs import Web

Web.resolv_url = staticmethod(ResolvUrl)

# DEPRECATED; compatibility ONLY
from web.resolvUrl import ResolvUrl as resolvUrl
from web.webs import WebDeprecated as web
