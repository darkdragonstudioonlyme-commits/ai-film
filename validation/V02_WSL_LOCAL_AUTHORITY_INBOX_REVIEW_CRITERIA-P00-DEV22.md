# V02 WSL-local authority inbox — review criteria

Independent review must verify the change is path-local only: all runtime consumers use the same WSL-local default inbox, explicit test overrides still work, manifest hashes bind exact bytes, trust/candidate identities are unchanged, no private key enters Git/inbox, missing authority stays fail-closed, and no native state advances.
