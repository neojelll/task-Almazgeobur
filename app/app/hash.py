import hashlib


async def hashed_file(file_content: bytes) -> str:
    hash_object = hashlib.sha256()
    hash_object.update(file_content)
    return hash_object.hexdigest()
