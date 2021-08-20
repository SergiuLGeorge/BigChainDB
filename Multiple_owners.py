from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from bigchaindb_driver.exceptions import MissingPrivateKeyError

bdb_root_url = 'http://127.0.0.1:9984'
bdb = BigchainDB(bdb_root_url)

alice, bob = generate_keypair(), generate_keypair()


car_asset = {
    'data': {
        'car': {
            'vin': '5YJRE11B781000196'
        }
    }
}

car_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=(alice.public_key, bob.public_key),
    recipients=(alice.public_key, bob.public_key),
    asset=car_asset,
)

signed_car_creation_tx = bdb.transactions.fulfill(
    car_creation_tx,
    private_keys=[alice.private_key, bob.private_key],
)

sent_car_tx = bdb.transactions.send_commit(signed_car_creation_tx)

carol = generate_keypair()
output_index = 0
output = signed_car_creation_tx['outputs'][output_index]

input_ = {
     'fulfillment': output['condition']['details'],
     'fulfills': {
         'output_index': output_index,
         'transaction_id': signed_car_creation_tx['id'],
     },
     'owners_before': output['public_keys'],
}

print(input_)

transfer_asset = {'id': signed_car_creation_tx['id'], }

car_transfer_tx = bdb.transactions.prepare(
     operation='TRANSFER',
     recipients=carol.public_key,
     asset=transfer_asset,
     inputs=input_,
)

signed_car_transfer_tx = bdb.transactions.fulfill(
     car_transfer_tx, private_keys=[alice.private_key, bob.private_key]
)

try:
    signed_car_transfer_tx = bdb.transactions.fulfill(car_transfer_tx, private_keys=alice.private_key,)
except MissingPrivateKeyError as e:
    print(e, e.__cause__, sep='\n')

print(bob.public_key)

sent_car_transfer_tx = bdb.transactions.send_commit(signed_car_transfer_tx)
print(sent_car_transfer_tx)
