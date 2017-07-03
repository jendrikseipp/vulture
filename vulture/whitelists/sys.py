from whitelist_utils import Whitelist

# Never report redirected streams as unused.
whitelist_sys = Whitelist()
whitelist_sys.stderr
whitelist_sys.stdin
whitelist_sys.stdout
