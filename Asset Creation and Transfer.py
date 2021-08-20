from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair

bdb_root_url = 'https://test.ipdb.io'

# creating an object of class BigchainDB
# If the BigchainDB node or cluster doesn’t require authentication tokens
bdb = BigchainDB(bdb_root_url)

# If it does require authentication tokens, you can do put them in a dict like so:
# tokens = {'app_id': 'your_app_id', 'app_key': 'your_app_key'}
# bdb = BigchainDB(bdb_root_url, headers=tokens)

# Alice and Bob are represented by public/private key pairs
alice, bob = generate_keypair(), generate_keypair()

print(f"\nAlice(private/public): {alice.private_key}, {alice.public_key}")
print(f"Bob(private/public): {bob.private_key}, {bob.public_key}")

# As an example, let’s consider the creation and transfer of a digital asset that represents a bicycle
bicycle_asset = {
    'data': {
        'bicycle': {
            'serial_number': 'abcd1234',
            'manufacturer': 'bkfab'
        },
    },
}

# You can optionally add metadata to a transaction. Any dictionary is accepted
bicycle_asset_metadata = {
    'planet': 'earth'
}

print(f"\nBicycle Asset: {bicycle_asset}")
print(f"Metadata: {bicycle_asset_metadata}")

# alice is the owner of the bicycle
# the public key verifies that the signed transaction is indeed signed by the one who claims
# to be the signee
prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=alice.public_key,
    asset=bicycle_asset,
    metadata=bicycle_asset_metadata
)

# the transaction is prepared
print(f"\nPrepared Creation: {prepared_creation_tx}")

# the transaction needs to be fulfilled
# alice needs to sign the transaction with her private key
fulfilled_creation_tx = bdb.transactions.fulfill(
    prepared_creation_tx,
    private_keys=alice.private_key
)
# the transaction is fulfilled by signing it with Alice’s private key
print(f"\nFulfilled Creation: {fulfilled_creation_tx}")

# sending it over to a BigchainDB node
sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)
print(f"\nSent Creation: {sent_creation_tx}")

# transaction id
txid = fulfilled_creation_tx['id']

# checking if the transaction was included in a block
# it returns the block height containing the transaction
# if the transaction is not in any block, None is returned
# if the transaction was invalid or could not be sent an exception is raised
block_height = bdb.blocks.get(txid=txid)

# retrieving the block containing the transaction
# if we want tos see the whole block, we can use the block height to retrieve the block itself
block = bdb.blocks.retrieve(str(block_height))
print(f"\nBlock height: {block_height}\nBlock: {block}")

# we want to transfer the asset from alice (owner) to bob
# alice could retrieve the transaction
creation_tx = bdb.transactions.retrieve(txid)
# or creation_tx = fulfilled_creation_tx
print(f"\nCreation: {creation_tx}")

# to prepare the transfer transaction, we need to know the id of the asset we'll be transfering
# because alice is consuming a CREATE transaction [SPECIAL CASE] the asset id IS NOT found on the asset itself
# IT IS simply the CREATE transaction's id
asset_id = creation_tx['id']

transfer_asset = {
    'id': asset_id
}

print(f"\nTransfer Asset: {transfer_asset}")

# preparing the transfer transaction
output_index = 0
output = fulfilled_creation_tx['outputs'][output_index]
print(f"\nOutput: {output}")
transfer_input = {
    'fulfillment': output['condition']['details'],
    'fulfills': {
        'output_index': output_index,
        'transaction_id': fulfilled_creation_tx['id']
    },
    'owners_before': output['public_keys']
}
print(f"\nTransfer Input: {transfer_input}")

prepared_transfer_tx = bdb.transactions.prepare(
    operation='TRANSFER',
    asset=transfer_asset,
    inputs=transfer_input,
    recipients=bob.public_key,
)
print(f"\nPrepared Transfer: {prepared_transfer_tx}")

# Fulfilling the transfer transaction
fulfilled_transfer_tx = bdb.transactions.fulfill(
    prepared_transfer_tx,
    private_keys=alice.private_key,
)
print(f"\nFulfilled Transfer: {fulfilled_transfer_tx}")

# sending the transaction to the connected BDB node
sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)
print(f"\nSent Transfer: {sent_transfer_tx}")

# we considered Alice’s case of consuming a CREATE transaction as a special case
# In order to obtain the asset id of a CREATE transaction, we had to use the CREATE transaction’s id:
# (e.g transfer_asset_id = create_tx['id'])
# if we wanted to consume TRANSFER transactions (e.g. fulfilled_transfer_tx) we could obtain the asset id from the
# asset['id'] property (e.g. transfer_asset_id = transfer_tx['asset']['id'])

# checking the previous and the current owner of the asset
print("\nIs Bob the owner? -->", sent_transfer_tx['outputs'][0]['public_keys'][0] == bob.public_key)
print("Was Alice the previous owner? -->", fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == alice.public_key)

