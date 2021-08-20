from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair

bdb_root_url = 'https://test.ipdb.io'

bdb = BigchainDB(bdb_root_url)

# All assets in BigchainDB become implicitly divisible if a transaction contains more than one of that asset
# Bob is now the owner of the asset, and he wants to rent it
# We need to create a time sharing token ( 1 token = 1 hour of riding)
bicycle_token = {
     'data': {
         'token_for': {
             'bicycle': {
                 'serial_number': 'abcd1234',
                 'manufacturer': 'bkfab'
             }
         },
         'description': 'Time share token. Each token equals one hour of riding.',
     },
}
print(f"Bicycle Token: {bicycle_token}")

# Bob has decided to issue 10 tokens and to assign them to Carly
# We denote Carly as receiving 10 tokens by using the tuple ([carly.public_key], 10)
bob, carly = generate_keypair(), generate_keypair()

# preparing the transaction
prepared_token_tx = bdb.transactions.prepare(
     operation='CREATE',
     signers=bob.public_key,
     recipients=[([carly.public_key], 10)],
     asset=bicycle_token,
)
print(f"\nPrepared Transaction: {prepared_token_tx}")

# fulfilling the transaction
fulfilled_token_tx = bdb.transactions.fulfill(prepared_token_tx, private_keys=bob.private_key)
print(f"\nFulfilled Transaction: {fulfilled_token_tx}")

# sending the transaction
sent_token_tx = bdb.transactions.send_commit(fulfilled_token_tx)
print(f"\nSent transaction: {sent_token_tx}")
print("\nSent token == Fulfilled token -->", sent_token_tx == fulfilled_token_tx)

# For this query we need to provide an asset_id and we will get back a
# list of transactions that use the asset with the ID asset_id
print(f"\nQuery Transaction: {bdb.transactions.get(asset_id=sent_token_tx['id'])}")
# Please note that the id of an asset in BigchainDB is actually the id of the transaction which created the asset.
# In other words, when querying for an asset id with the operation set to CREATE,
# only one transaction should be expected.
# This transaction will be the transaction in which the asset was created,
# and the transaction id will be equal to the given asset id.

# If you were busy sharing your bicycle with the whole city you might have a really long list.
# So let’s limit the results and just see the CREATE transaction.
print(f"\nLimit Query: {bdb.transactions.get(asset_id=sent_token_tx['id'], operation='CREATE')}")
