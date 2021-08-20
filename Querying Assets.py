from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair

bdb_root_url = 'https://test.ipdb.io'

bdb = BigchainDB(bdb_root_url)

alice = generate_keypair()

# creating 3 assets
hello_1 = {'data': {'msg': 'Hello BigchainDB 1!'}, }
hello_2 = {'data': {'msg': 'Hello BigchainDB 2!'}, }
hello_3 = {'data': {'msg': 'Hello BigchainDB 3!'}, }

print(f"Hello_1: {hello_1}")
print(f"Hello_2: {hello_2}")
print(f"Hello_3: {hello_3}\n")

# set the metadata to query for it in an example below
metadata = {'planet': 'earth'}
print(f"Metadata: {metadata}\n")

# preparing the CREATE transaction
prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=alice.public_key,
    asset=hello_1
)
print(f"Prepared Creation: {prepared_creation_tx}")

# fulfilling the CREATE transaction
fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx, private_keys=alice.private_key)
print(f"Fulfilled Creation: {fulfilled_creation_tx}\n")

# sending the CREATE transaction
bdb.transactions.send_commit(fulfilled_creation_tx)

# doing the same thing two more times
prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=alice.public_key,
    asset=hello_2
)
print(f"Prepared Creation: {prepared_creation_tx}")

fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx, private_keys=alice.private_key)
print(f"Fulfilled Creation: {fulfilled_creation_tx}\n")

bdb.transactions.send_commit(fulfilled_creation_tx)

prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=alice.public_key,
    asset=hello_3
)
print(f"Prepared Creation: {prepared_creation_tx}")

fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx, private_keys=alice.private_key)
print(f"Fulfilled Creation: {fulfilled_creation_tx}\n")

bdb.transactions.send_commit(fulfilled_creation_tx)

# Querying for assets
print(f"Querying Assets: {bdb.assets.get(search='bigchaindb')}")
# This call returns all the assets that match the string bigchaindb, sorted by text score, as well as the asset id.
# This is the same id of the transaction that created the asset.
# It’s also possible to limit the amount of returned results using the limit argument:
print(f"Limit Query: {bdb.assets.get(search='bigchaindb', limit=2)}\n")

# Querying for metadata
# This query is similar to the asset query. The search is applied to all the strings inside the metadata and returns
# all the metadata that match a given text search string. The only difference is the returned id.
# The id of the asset query is the same id of the transaction that created the asset.
# Whereas the id of the metadata is the same id of the transaction where it was defined.
# In the Querying for Assets example we already set the metadata for the three transactions.
# Let’s perform a text search for all metadata that contain the word earth:
print(f"Querying Metadata: {bdb.metadata.get(search='earth')}")
# This call returns all the metadata that match the string earth, sorted by text score, as well as the transaction id.
# It’s also possible to limit the amount of returned results using the limit argument:
print(f"Limit Query: {bdb.metadata.get(search='earth', limit=2)}")
