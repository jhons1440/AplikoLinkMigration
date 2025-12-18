def create_link(event: dict):
    url = f'https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key={settings.FIREBASE_API_KEY}'
    request_data = {
        "dynamicLinkInfo": {
            "domainUriPrefix": settings.FIREBASE_DOMAIN_PREFIX_URL,
            "link": event['link'],
            "androidInfo": {
                "androidPackageName": settings.MOBILE_APP_PACKAGE_NAME
            },
            "iosInfo": {
                "iosBundleId": settings.MOBILE_APP_PACKAGE_NAME,
                "iosAppStoreId": settings.APPLE_STORE_APP_ID
            },
            "navigationInfo": {
                "enableForcedRedirect": True,
            },
            "socialMetaTagInfo": {
                "socialTitle": event['title'],
                "socialDescription": event['description'],
                "socialImageLink": event['image_url'] if event['image_url'] else static('img/logo.png'),
            }
        },
        "suffix": {
            "option": "SHORT"
        }
    }

    r = requests.post(url=url, data=json.dumps(request_data))
    if r.status_code != 200:
        logger.error({
            'ref': 'Error while creating dynamic link',
            'event_title': event['title'],
            'res_data': r.json()
        })
        dynamic_url = None
    else:
        dynamic_url = r.json()['shortLink']
    return dynamic_url
