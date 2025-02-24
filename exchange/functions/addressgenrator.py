import uuid

def generate_contract_address():
    return uuid.uuid4().hex[:40]
