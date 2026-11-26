# SOS Bridge – tested Windows programs

**SOS Bridge** runs Windows programs on Simple OS (from 1.2): double-click a `.exe` or `.msi` file, or right-click →
"Run with SOS Bridge". It is the free app [Bottles](https://usebottles.com) with Wine. Wine doesn't run every Windows
program, so this page lists the programs that are **known** to work – tested by us or reported by people who use
it – and the ones that don't. Your program isn't listed? It may still work. Try it, then
[tell us how it went](#report-a-program).

Last updated: 26 November 2026 (Simple OS 1.2).

## Tested programs

**Works** installs, starts and does its job · **Starts** installs and opens, its main job wasn't checked yet ·
**No** doesn't work · **–** not tested yet

| Program | Version | Kind | Install | Starts | Checked | Uninstall | Result |
|---|---|---|---|---|---|---|---|
| 7-Zip | 26.06 (64-bit `.exe` and `.msi`, 32-bit `.exe`) | archiver | Yes | Yes | create and extract an archive | Yes | **Works** |
| Notepad++ | 8.9.9.1 (installer and portable `.zip`) | text editor | Yes | Yes | type and save, open from Downloads | Yes | **Works** |
| WinSCP | 6.7.1 | file transfer (SFTP) | Yes | Yes | download and upload over SFTP | Yes | **Works** |
| PuTTY | 0.85 (`.msi`) | SSH client | Yes | Yes | log in over SSH, run a command | Yes | **Works** |
| SumatraPDF | 3.6.1 | PDF reader | Yes | Yes | open a PDF | Yes | **Works** |
| KeePass | 2.62 (.NET) | password manager | Yes | Yes | create and save a database | Yes | **Works** |
| Greenshot | 1.3 (.NET) | screenshots | Yes | Yes | take a screenshot and save it (it sits in the tray) | Yes | **Works** |
| GIMP | 3.0.8 | image editor | Yes | Yes | convert PNG to JPG | Yes | **Works** ¹ |
| Inkscape | 1.4.4 | vector drawing | Yes | Yes | export SVG to PNG | Yes | **Works** ¹ |
| LibreOffice | 26.8.3 (`.msi`) | office suite | Yes | Yes | Writer: text to PDF | Yes | **Works** ¹ |
| Python | 3.14.10 | programming | Yes | Yes | IDLE: a script writes a file | Partly ² | **Works** |
| DB Browser for SQLite | 3.13.1 (with Visual C++ 2015–2022) | database | Yes | Yes | open a database | Yes | **Works** |
| VLC | 3.0.24 | media player | Yes | Yes | – | Yes | **Starts** ¹ |
| Audacity | 4.0.2 (`.msi`) | audio editor | Yes | Yes | – | Yes | **Starts** ¹ |
| Visual Studio Code | 1.147 | code editor | Yes | No | – | Yes | **No** ³ |
| Obsidian | 1.15.1 | notes | No | – | – | – | **No** ³ |
| FileZilla | – | file transfer (FTP) | – | – | – | – | **–** |

All programs above also started again after restarting the computer, and their entries appear in the Simple OS menu
like any other app. Their Open and Save windows show your own Documents, Downloads, Pictures, Music, Videos and
Desktop.

1. **There's a Simple OS version.** GIMP, Inkscape, LibreOffice, VLC and Audacity also exist as normal Simple OS apps
   in the Software Center – they start faster and fit in better. SOS Bridge points you to them when you open their
   Windows installer. You can still continue with the Windows version.
2. **Python:** uninstalling failed once in the test (error 0x80070643), most likely because the test had removed parts
   of it by hand before.
3. **Electron apps** (programs built on Chromium, such as Visual Studio Code and Obsidian) crash in Wine or their
   installer doesn't finish. Use the Simple OS versions instead: **VSCodium** (Setup Wizard → Extras → Developer
   Tools, or the Software Center) is Visual Studio Code without Microsoft's tracking, and Obsidian is in the Software
   Center.

### How we test

Each program is tested in a fresh Simple OS 1.2 installation with SOS Bridge (Bottles 67.7 from Flathub, runner
soda-11.0-10), set up by SOS Bridge itself on the first double-click:

1. Open the downloaded installer with a double-click and install it (as a normal user would).
2. Start it from the Simple OS menu and check one real job (save a file, open a document, connect to a server …).
3. Restart the computer and start it again.
4. Uninstall it with its own uninstaller – the menu entry has to disappear too.

The test run is documented in issue [#153](https://github.com/FreakySneaky787/Simple-OS/issues/153) (24 November
2026).

## What never works

- **Programs made for Windows itself:** Windows installation media and setup tools, drivers, antivirus and system
  tuners. They need a real Windows.
- **Microsoft 365** (Word, Excel, Outlook as apps) and **current Adobe apps** (Photoshop, Premiere, Acrobat Pro).
  Microsoft 365 works in the browser; LibreOffice or ONLYOFFICE open Word and Excel files.
- **Games with kernel anti-cheat** (e.g. Valorant, Fortnite, many competitive online games). Many other games run
  through Steam: in Steam → Settings → Compatibility, turn on "Steam Play for all other titles".

## Good to know

- The first double-click sets SOS Bridge up once – that takes about a minute. After that programs open straight away.
- Windows' own MSI setup windows sometimes show placeholder text ("Lorem ipsum") on the "Custom Setup" page. That
  comes from Wine and is harmless.
- Links in Windows programs open in your normal Simple OS browser.
- Menu → Help → Windows Programs on Simple OS explains the same in your language, with alternatives.

## Report a program

Tried a Windows program with SOS Bridge? Open an
[issue on GitHub](https://github.com/FreakySneaky787/Simple-OS/issues/new?title=SOS%20Bridge%3A%20) with the program's
name and version, where you downloaded it, and what worked: installing, starting, its main job, starting again after
a restart, uninstalling. If something didn't work, the exact error message helps a lot. The program then gets a row
here.
