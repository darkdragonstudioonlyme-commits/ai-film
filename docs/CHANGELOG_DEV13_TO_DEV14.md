# CHANGELOG — dev13 → dev14

## Network transport

- Add pure/testable proxy-context policy shared by fixed agent and controller parser.
- Configured guest env proxy / Windows WinHTTP or user proxy returns normalized network exit14.
- Controller environment proxy blocks before child launch.
- Controller revalidates proxy observations in returned evidence.
- Keep endpoint `proxy_mode=DIRECT`; non-DIRECT adapter requests remain unapproved.
- No DNS/firewall/VPN/proxy/CA changes.

## Tests

- Added 10 focused transport tests.
- Final author regression: 739 PASS; static: 96 PASS; native Windows/WSL/LAB/SITE: NOT_RUN.

## Contracts

No FD/D00/public-contract change. The implementation docs' old “non-DIRECT adapter” wording is corrected to match exact V2/RD00-03.
