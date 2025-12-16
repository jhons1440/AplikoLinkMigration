
def _make_requests_session(retries = 2, backoff = 0.15, status_forcelist = (429, 500, 502, 503, 504)):
    """
    Create a Session with a small retry policy and a polite User-Agent.
    """
    s = requests.Session()
    retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=status_forcelist, allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"]))
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"User-Agent": "firebase-link-inspector/1.0"})
    return s



def get_final_url(short_link):
    session = _make_requests_session()
    cur, chain, visited = short_link, [], set()

    for _ in range(12):
        if cur in visited:
            return None
        visited.add(cur)

        resp = session.get(cur, allow_redirects=False, timeout=5, stream=True)
        loc = resp.headers.get("Location")
        chain.append({"requested_url": cur, "status_code": resp.status_code, "location_header": loc})

        if 300 <= resp.status_code < 400 and loc:
            resp.close()
            cur = urljoin(cur, loc)
            continue

        final_url = chain[-1]["resolved_url"] = resp.url
        break
    else:
        return None

    return final_url


def extract_dynamic_link_metadata__(short_link):
    data = {}
    out = {}

    final_url = get_final_url(short_link)
    data["link"] = final_url
    data["old_link"] = short_link


    try:
        headers = {"User-Agent": "python-requests/firebase-dl-inspector/1.0"}
        resp = requests.get(short_link, headers=headers, timeout=5, stream=True)
        history = list(resp.history) + [resp]
        param_sources: List[Dict[str, str]] = []
        
        for r in history:
            params = {k: v[0] for k, v in parse_qs(urlparse(r.url).query).items()}
            param_sources.append(params)

        mappings = {
            "socialMetaTagInfo": {
                "socialTitle": ["st", "socialTitle"],
                "socialDescription": ["sd", "socialDescription"],
                "socialImageLink": ["si", "socialImageLink", "socialImageUrl"]
            },
            "androidInfo": {k: [k] for k in ["apn", "afl", "amv"]},
            "iosInfo": {k: [k] for k in ["ibi", "isi", "ifl"]}
        }


        for category, key_map in mappings.items():
            extracted = {}
            for target_key, candidates in key_map.items():
                for src in param_sources:
                    found = next((src[c] for c in candidates if c in src), None)
                    if found:
                        extracted[target_key] = found
                        break
            
            if extracted:
                out[category] = extracted

        resp.close()

    except Exception as ex:
        out["reconstructed"]["error"] = f"{type(ex).__name__}: {ex}"

    data["title"] = out.get("socialMetaTagInfo").get("socialTitle")
    data["description"] = out.get("socialMetaTagInfo").get("socialDescription")
    data["image_url"] = out.get("socialMetaTagInfo").get("socialImageLink")
    data["androidInfo"] = out.get("androidInfo")
    data["iosInfo"] = out.get("iosInfo")
    data["short_code"] = extract_shortcode(short_link)    

    return data

