import os

# @has_checkpoints

print("HELLO")
wid = 9
rid = 8
bid = 5
# @checkpoint write_buffer wid bid 1
# @checkpoint read_buffer rid bid 1
print("BYE")
