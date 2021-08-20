from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair

bdb_root_url = 'http://127.0.0.1:9984'

bdb = BigchainDB(bdb_root_url)

bicycle = {
     'data': {
         'bicycle': {
             'serial_number': 'abcd1234',
             'manufacturer': 'bkfab',
         },
     },
}

metadata = {'planet': 'earth'}
alice, bob = generate_keypair(), generate_keypair()
prepared_creation_tx = bdb.transactions.prepare(
     operation='CREATE',
     signers=alice.public_key,
     asset=bicycle,
     metadata=metadata,
)
fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx, private_keys=alice.private_key)
sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)
print(sent_creation_tx)