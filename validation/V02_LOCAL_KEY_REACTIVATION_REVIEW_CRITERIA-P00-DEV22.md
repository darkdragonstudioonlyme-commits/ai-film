# V02 dev22 local-key reactivation review criteria

Review must verify the V02-LOCAL-KEY-PARITY-001 forensic finding, confirm the previous 5d595732... activation is unusable rather than silently substituted, verify the durable 7f14c158... key's public metadata and mode without exposing private bytes, independently run the new key-parity regression and live verifier, verify trust/signature/manifest pinning, rerun all V02 regressions and exact-dev22 CI, and confirm zero native execution.
