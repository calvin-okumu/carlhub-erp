from hashids import Hashids

# Initialize hashids with a salt for security
hashids = Hashids(salt='django-crm-salt', min_length=8)

def encode_id(id_value):
    """
    Encode an integer ID to a hashid string.
    """
    return hashids.encode(id_value)

def decode_id(hashid):
    """
    Decode a hashid string back to integer ID.
    Returns None if invalid.
    """
    decoded = hashids.decode(hashid)
    return decoded[0] if decoded else None