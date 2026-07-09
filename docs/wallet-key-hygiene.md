# Multisig Wallet Key Hygiene

Generic process for an organisation holding a crypto treasury in an N-of-M
multisig wallet (configured in `org.yml` under `wallet:`). The goal: no single
person, device failure, or accident can lose or move the funds.

## Principles

1. **No key material is ever digital-adjacent to governance records.** Seed
   words, passphrases, and extended private keys never appear in documents,
   chat, email, photos, cloud storage, or password managers shared with the
   committee. Health-check records capture pass/fail only.
2. **Separation of holders.** Each of the M keys is held by a different
   committee member, on separate hardware, with seed backups stored in
   separate physical locations. No holder stores another holder's backup.
3. **Watch-only everywhere else.** The treasurer and committee monitor the
   balance via a watch-only wallet built from the public output descriptor.
   The descriptor itself (public, but privacy-sensitive) is backed up in at
   least two places — losing it makes recovery painful even with N seeds.
4. **Signing is deliberate.** Spends are authorised by committee resolution
   (minuted), then signed by N holders. No holder signs a transaction they
   did not see resolved.

## Regular health check

On the cadence in `wallet.check_cadence` (quarterly recommended), run the
checklist generated from `templates/wallet-check.md.j2`:

```bash
python3 scripts/generate.py --template wallet-check --date YYYY-MM-DD
```

Each holder confirms: device located and unlocks, firmware reviewed, seed
backup physically intact, and a test signature (sign a PSBT — no broadcast
needed). Shared checks confirm the descriptor backup and that the watch-only
balance reconciles with finance records. File the completed record with the
org's governance documents and add any failures to the actions register.

## Personnel changes

When a key holder leaves the committee (or a device/backup is compromised or
lost): treat it as a key rotation, not an ordinary handover. Create a new
wallet with a fresh key for the replacement holder and sweep the funds by
committee resolution. Never transfer an existing seed to a new person.

## Verification

- Dry-run: generate the checklist with `--stdout` against `org.example.yml`
  and confirm each configured holder gets a section.
- The real test is the quarterly check itself — a failed check is the process
  working, not failing: log it and fix it.
