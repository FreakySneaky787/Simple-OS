# Maintaining Simple OS

How Simple OS is released and kept alive, written so that someone else *could* take over if needed (issue #94).
Today one person does everything; this page is there so that no step lives only in one head. It contains no secrets.

## 1. What runs on its own, and what doesn't

| | Keeps working without the maintainer? |
|---|---|
| **Debian updates** (security fixes, Firefox ESR, kernel …) on installed systems | **yes** – they come straight from Debian, not from this project |
| Apps from the Software Store (Flathub) | **yes** |
| **New Simple OS editions** (the package `simpleos`) | **no** – only the maintainer can sign them (section 3) |
| The download (ISO) and the website | yes, as long as the GitHub account exists |

So if nothing happens here for a while, installed systems stay safe until Debian 12 support ends (Debian LTS, June
2028). Only new Simple OS features and fixes stop.

## 2. Releasing an edition (1.0.x, 1.x)

The details are in [TESTING.md](../TESTING.md) (checklist) and the README section
[Updates to new Simple OS editions](../README.md#updates-to-new-simple-os-editions). In short:

1. **Plan:** a milestone per release on GitHub (e.g. "1.0.7"), the date in [ROADMAP.md](../ROADMAP.md) and on the
   website's roadmap page. Cadence: bugfix every 2–3 weeks, feature release every 2–3 months (ROADMAP "How we release").
2. **Work:** bugfixes for the next 1.0.x on `main`, new features on `next` (section 7). `main` is pushed only on
   release day, so it always matches the published edition; `next` is pushed as the work goes on. Close issues when
   the work is done and tested ("done, ships in X.Y.Z"), project board item → Done; things that need real hardware stay
   open with the label `verify`.
3. **Version:** `./tools/release.sh version X.Y.Z`, then `RELEASE_NOTES.md` (it is the release text and the target of
   the installer's "Known issues" button), the "What's new" text (`config/includes.chroot/usr/share/simpleos/whats-new`),
   the ROADMAP table, a TESTING section.
4. **Release day:** `git fetch origin` (merge if something was changed on GitHub), `git push`.
5. **Build:** `sudo ./build_iso.sh` (Podman container from `Containerfile`, log in `build/build.log`; the verify hook
   must end with `Simple OS verify: OK`). Then `cd output && sha256sum -c Simple-OS.iso.sha256`. Build as often as
   needed: the package version carries the build time (`X.Y.Z+YYYYMMDDHHMMSS`), so machines installed from an earlier
   test build still get the published build. Careful: `./build_iso.sh --config-only` also rebuilds `output/repo` –
   never run it between the final build and `publish`.
6. **Test:** TESTING.md – at least a fresh VM install (BIOS and UEFI) and an **update from the previous release**
   through Software Updates (a VM installed from the old ISO).
7. **Publish:** `./tools/release.sh sign && ./tools/release.sh publish` (asks for the key's passphrase). Use
   `publish --no-iso` when neither the installer nor hardware detection changed – the old ISO stays the download.
   `publish` creates a draft, uploads the ISO and the signed repository, checks everything, and only then marks it as
   "latest" – from that moment installed systems are offered the new edition.
8. **After publishing:** the website (section 6), close the milestone, an announcement in Discussions → Announcements
   (title "Simple OS X.Y.Z is out", the previous one is the template), thank testers in their issues. Merge `main` into
   `next` and `trixie` (section 7).

Never publish a "latest" release without the repository files – `publish` refuses it, because it would break
"Check for updates" on every installed system.

## 3. The release signing key

Installed systems only accept Simple OS updates signed with this key:

```
Simple OS Release Signing Key   ed25519, created 2026-10-06, does not expire
Fingerprint: F5F7 17EB B8B4 F372 49E6  9022 81DB EC50 266B 69EB
```

- **Public key:** `config/includes.chroot/usr/share/keyrings/simpleos-archive-keyring.asc` (in every image and in the
  package `simpleos`).
- **Private key:** on the maintainer's computer in `~/.local/share/simpleos-release/gnupg`, protected by a
  passphrase. A **backup** of it exists outside that computer (encrypted cloud storage). Where exactly, and the
  passphrase, are never written into this repository.
- **Check the backup** now and then: restore it into an empty directory and sign a test file –
  `SIMPLEOS_GNUPGHOME=/tmp/keytest` + `gpg --import`, `gpg --clearsign`, then delete `/tmp/keytest`.

**Changing the key (rotation)** – only while the old key still exists:

1. Create the new key in a separate `GNUPGHOME` and add its public key **next to** the old one in
   `simpleos-archive-keyring.asc` (one file, both keys).
2. Release that as a normal edition, still signed with the **old** key. Installed systems now trust both keys.
3. Wait until most systems have updated (at least one more release cycle), then sign with the new key and remove the
   old public key in a later release.

**If the private key is lost:** installed systems can no longer get Simple OS updates through Software Updates
(Debian's updates keep working). The only way back is a new key that users install by hand (download the new
keyring package and check its fingerprint against an announcement), or a reinstall from a new ISO. That is why the
backup matters more than anything else in this project.

## 4. Issues, labels, milestones

- **New issue:** reproduce if possible (VM), ask for the report file from Menu → Help → Report a Problem, then label
  and give it a milestone:
  - `bug` – something doesn't work; hotfix if it breaks starting, installing, data, security or Wi-Fi/sound/login,
    otherwise the next bugfix release.
  - `enhancement` + `roadmap` – planned feature, milestone 1.1/1.2/2.0; `idea` – not scheduled (milestone "Ideas").
  - `verify` – needs a check on real hardware; `debian-13` – part of 2.0; `accessibility`; `documentation`.
  - `good first issue` / `help wanted` – for newcomers (section 5).
- **Project board:** "Simple OS Roadmap" (GitHub project 2), Status Todo → In Progress → Done.
- **Questions** belong in Discussions (Q&A), not in issues – move them politely.
- Be kind; the [Code of Conduct](../CODE_OF_CONDUCT.md) applies. Security reports come in privately
  ([SECURITY.md](../SECURITY.md)) – fix them first, publish the details after the release.

## 5. Good tasks for newcomers

No code needed for most of them:

- **Hardware reports:** install on a computer and report what works (issue #49, label `verify`).
- **Docs:** typos, clearer help texts, screenshots for the help pages.
- **Translations** of Simple OS's own tools – planned for 1.1 (#43); say which language in Discussions.
- Small bugs with the label `good first issue`.

## 6. Website

The website is its own repository, `FreakySneaky787/FreakySneaky787.github.io` (GitHub Pages, plain HTML). After
every release – and only after `publish`, because the links point to the new release:

- `download.html`: version, date, ISO size, SHA-256 (from `output/Simple-OS.iso.sha256`), links to `vX.Y.Z`.
- `index.html`: news, version, "Coming next"; `simple-os.html`: version history row.
- `roadmap.html`: mirrors ROADMAP.md (release marked "Released", next date).

## 7. Branches

- `main` – the published Simple OS 1.x edition on Debian 12, plus the bugfixes for the next 1.0.x release. Releases are
  tagged `vX.Y.Z` on it; it is pushed on release day only.
- `next` – **the branch for new features**: everything for the next feature release (1.1, 1.2 …). Pushed as the work
  goes on, so others can follow it. Test ISOs are built from it like from `main` (the package version carries the build
  time, so test systems still get the published build later).
  - After every bugfix release: `git switch next && git merge main` – the fixes reach the new features.
  - Feature release: when `next` is tested (TESTING.md), `git switch main && git merge next` (a fast-forward if `main`
    got no fixes in the meantime), then release from `main` as in section 2.
  - Docs that are already true for the published edition (website links, issue forms) may go to `main` directly.
  - `next` says what it is: it carries the version of the coming feature release (`./tools/release.sh version 1.1`,
    with its "What's new" notes – test ISOs from `next` show "Simple OS 1.1"), and a notice at the top of `README.md`
    (marker `simpleos-next-branch`). Before the feature release: write `RELEASE_NOTES.md` for it and remove the notice –
    `./tools/release.sh publish` refuses otherwise. When `next` starts the following feature release, both come back.
  - Merging a bugfix release (`main`, e.g. 1.0.8) into `next` conflicts in `usr/lib/os-release`, the installer branding
    and `whats-new`: keep `next`'s version, and add the bugfix's notes to its "What's new" if they matter.
- `trixie` – Simple OS 2.0 "Rigi" on Debian 13 (ROADMAP "2.0"). Merge `main` into it regularly so fixes are not lost.
  Before 2.0 is published, 1.x systems need their own update channel (ROADMAP, issue #52).

## 8. Accounts and access

- GitHub account `FreakySneaky787`: owns the repository, the releases (= the update channel of every installed
  system: `https://github.com/FreakySneaky787/simple-os/releases/latest/download/`), the website and Discussions.
  Keep two-factor authentication on and the recovery codes in a safe place.
- A fork elsewhere could continue the code, but **not** the updates of already installed systems – they only look at
  this repository's releases and only trust the key in section 3.
