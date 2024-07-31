blacklisted_items = []

def add_to_blacklist(item):
    if item not in blacklisted_items:
        blacklisted_items.append(item)

def is_blacklisted(item):
    return item in blacklisted_items
