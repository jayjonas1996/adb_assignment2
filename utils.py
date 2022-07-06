import json

def append_room_id(r, id):
    if r.exists('rooms'):
        rooms = json.loads(r.get('rooms'))
        rooms.append(id)
        rooms = list(set(rooms))
        r.set('rooms', json.dumps(rooms))
    else:
        r.set('rooms', json.dumps([id]))

def list_rooms(r):
    if r.exists('rooms'):
        return json.loads(r.get('rooms'))
    else:
        return []

def r_get(r, key):
    return json.loads(r.get(key))

def r_set(r, key, data):
    r.set(key, json.dumps(data))
