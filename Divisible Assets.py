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

# Bob is the one that supplies/distributes the tokens
print("\nFormer tokens owner is Bob -->", fulfilled_token_tx['inputs'][0]['owners_before'][0] == bob.public_key)
# Carly is the owner of 10 tokens now
print("Current tokens owner is Carly -->", fulfilled_token_tx['outputs'][0]['public_keys'][0] == carly.public_key)
print("Amount of tokens == 10 -->", fulfilled_token_tx['outputs'][0]['amount'] == '10')

# Now in possession of the tokens, Carly wants to ride the bicycle for two hours.
# To do so, she needs to send two tokens to Bob:
output_index = 0
output = fulfilled_token_tx['outputs'][output_index]
print(f"\nOutput: {output}")

transfer_input = {
     'fulfillment': output['condition']['details'],
     'fulfills': {
         'output_index': output_index,
         'transaction_id': fulfilled_token_tx['id'],
     },
     'owners_before': output['public_keys'],
 }
print(f"\nTransfer Input: {transfer_input}")

transfer_asset = {
     'id': fulfilled_token_tx['id'],
}
print(f"\nTransfer Asset: {transfer_asset}")

prepared_transfer_tx = bdb.transactions.prepare(
     operation='TRANSFER',
     asset=transfer_asset,
     inputs=transfer_input,
     recipients=[([bob.public_key], 2), ([carly.public_key], 8)]
)
print(f"\nPrepared Transfer: {prepared_transfer_tx}")

fulfilled_transfer_tx = bdb.transactions.fulfill(prepared_transfer_tx, private_keys=carly.private_key)
print(f"\nFulfilled Transfer: {fulfilled_transfer_tx}")

# Notice how Carly needs to reassign the remaining eight tokens to herself if she wants to only
# transfer two tokens (out of the available 10) to Bob.
# BigchainDB ensures that the amount being consumed in each transaction (with divisible assets) is the same
# as the amount being output. This ensures that no amounts are lost.
# The fulfilled_transfer_tx dictionary should have two outputs, one with amount='2' and the other with amount='8'

sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)
print("\nSent Transfer == Fulfilled Transfer -->", sent_transfer_tx == fulfilled_transfer_tx)
