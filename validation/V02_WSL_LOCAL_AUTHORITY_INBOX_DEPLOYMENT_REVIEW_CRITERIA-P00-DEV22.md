# V02 WSL-local authority inbox deployment — review criteria

Independent deployment review must verify the receipt matches observed WSL state, exact promoted manifest bytes are deployed, local identity context is unchanged, private/public key parity matches the deployed trust anchor without exposing private bytes, inbox/objects are WSL-local, private key is outside the inbox, preflight/intake remain fail-closed on missing approval, watcher is active/enabled, READY/native-policy are absent and no native execution occurred.
