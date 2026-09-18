# Phase00 dev22 — production-like migration operations runbook

This runbook is executable only after the exact migration design passes independent REVIEW/AUDIT and canonical validation CI. It changes the non-native production-like runtime/control plane only. `AI-FILM-P00-LAB` must remain stopped and all 86 native procedures remain NOT_RUN.

The canonical deployable control source is `validation/prodlike-dev22/`; do not recover or install units from prose, ad-hoc shell history or `/etc/systemd/system`. Units belong to the lingering `dragon` user manager. The exact V22 package/wheel are the accepted artifact identities in `release-control.json`.

Pre-switch evidence must capture current dev21 verify/health/status, user timer states, V02 missing/block state and a fresh dev21 control backup. Build/verify dev22 side-by-side first. Only after exact release and rebuild-set verification may the operator quiesce user timers, deploy exact reviewed control bytes, atomically switch `current`, re-enable target timers and run the reviewed producer sequence. Final readiness requires both independent control/user-systemd parity and runtime-health PASS; health alone is insufficient.

Rollback uses the private pre-switch root-control/user-unit/config/symlink snapshot and restores dev21 before re-enabling prior timers. A migration failure never permits V02/V03 advancement.
