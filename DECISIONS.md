# Decisions

## D-001 — Product-first pivot (2026-09-24)
Phase00 enterprise-style LAB/prodlike governance is frozen as historical evidence. The active goal is a 60–90 second vertical slice.

## D-002 — Delivery shape
Master 9:16; data/timeline remain aspect-neutral enough to re-render or reframe to 16:9.

## D-003 — Languages
Initial release languages are EN, ZH and VI. Image/video master is shared; dialogue, subtitle and lip-sync assets are language-specific.

## D-004 — Models and GPU
Generation models should be locally runnable/open-weight candidates with commercial-use review. GPU selection follows a fixed rental benchmark before hardware purchase.

## D-005 — Safety/authority
Preserve P00 history and WIP. No destructive cleanup, publication, or unbounded paid resource use is implied by Continue v2.

## D-006 — Freeze legacy P00 background timers (2026-09-24)
After PRODUCT_V2 activation, re-audit found 11 legacy aifilm-p00 user timers still enabled and active. They were disabled and stopped with systemctl --user disable --now. Unit files/evidence were preserved; this is reversible and prevents the frozen P00 control plane from generating new background state/evidence.
