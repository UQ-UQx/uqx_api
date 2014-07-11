import uqx_api.settings

def test_view(request):
    extra = {}
    extra['settings_brand'] = uqx_api.settings.BRAND
    extra['settings_brand_website'] = uqx_api.settings.BRAND_WEBSITE
    return extra