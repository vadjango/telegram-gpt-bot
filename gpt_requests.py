from db_interaction import get_all_api_keys

KEY_ACTIVE_REQUESTS: dict[str, int] = {}
for api_key, in get_all_api_keys():
    KEY_ACTIVE_REQUESTS[api_key] = 0
