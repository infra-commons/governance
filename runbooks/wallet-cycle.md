# Runbook: Wallet Health-Check Cycle

Cadence: `org.yml wallet.check_cadence` (quarterly recommended). Owner: the
key holders listed (by role) in `wallet.holders`, coordinated by the
Treasurer. Full policy: `docs/wallet-key-hygiene.md`.

## Steps

1. On the scheduled check date (automate via the `wallet-check` entry in
   `reminders.example.yml`), generate the checklist:
   ```bash
   python3 scripts/generate.py --template wallet-check --date YYYY-MM-DD
   ```
2. Each key holder completes their section: device located and unlocked,
   firmware reviewed, seed backup physically verified, PSBT test-signature
   produced. **No seed material is ever written into the record.**
3. Complete the shared checks: descriptor backup accessible, watch-only
   balance reconciles with finance records, personnel/device changes
   reviewed.
4. Record the outcome; add any failed check as an action in the actions
   register with an owner and deadline.
5. File the completed record with the org's governance documents (not in a
   public repo).

## Escalation

- A holder cannot produce a test signature or locate a backup → treat as a
  potential key loss: schedule remediation within 30 days; if unresolved,
  rotate to a new wallet per `docs/wallet-key-hygiene.md`.
- A holder leaves the committee → key rotation, never seed handover.

## Verification (dry-run)

- `python3 scripts/generate.py --template wallet-check --date 2099-01-05 --stdout --config org.example.yml`
  renders one section per configured holder.
- First live run: complete a full check off-cycle once to shake out missing
  backups before relying on the quarterly cadence.
