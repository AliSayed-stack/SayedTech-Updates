# SayedTech Updates

## Release 0.65
The updater manifest is in `latest.json`. Upload the prepared source archive as a GitHub Release asset with these exact values:

- Tag: `v0.65`
- Asset filename: `SayedTech_Stage1-0.65.zip`

The asset must be attached to release `v0.65`; the manifest already contains its HTTPS download URL and SHA-256. The repository must remain public for end-user update checks to fetch `latest.json` and the release asset without signing in.

The prepared archive contains the updater configuration pointing to this repository's raw `latest.json`.
