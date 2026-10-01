# SmoothTalker / Dr. Sbaitso synthesizer for NVDA

An NVDA speech synthesizer that runs the **original 1990 First Byte SmoothTalker
3.5 engine** — the voice from Creative Labs' *Dr. Sbaitso* — under the
[Unicorn](https://www.unicorn-engine.org/) CPU emulator.

Nothing here is a reimplementation. The real 16-bit DOS speech code executes,
driving what it believes is a Sound Blaster; the add-on emulates enough of the
DSP and the 8237 DMA controller to capture the audio the card would have played,
then converts it to 16-bit, resamples it to 22050 Hz and hands it to NVDA.

## Requirements

**NVDA 2026.1 or later.** NVDA became a 64-bit application in 2026.1, so the
bundled Unicorn build is 64-bit and this version will not run on earlier,
32-bit releases of NVDA.

## Install

Download `sbaitso-1.1.nvda-addon` from
[Releases](../../releases), then open it, or use NVDA's
*Tools → Add-on store → Install from external source*. Restart NVDA and pick
**smooth talker** in *NVDA menu → Preferences → Settings → Speech*.

## Settings

The engine keeps its settings in a five-word block that Dr. Sbaitso filled with
`0, 0, 5, 5, 5`. Four of those fields are exposed:

| Setting | Range | Effect |
| --- | --- | --- |
| Rate | 0–9 | 1.91 s to 0.81 s for a fixed phrase |
| Pitch | 0–9 | about 41 Hz to 154 Hz |
| Tone | 0/1 | on cuts the low end — thinner and brighter |
| Volume | 0–9 | quiet to loud; does not clip |

The sliders are declared over the engine's own 0–9 range rather than NVDA's
usual 0–100, so nothing is rescaled and every value the engine has is
individually reachable. The settings ring steps by one unit; page up and page
down in Voice settings move by three.

There is no inflection setting because the engine has no such control. It does
produce intonation of its own accord — pitch moves over roughly 48–110 Hz within
an utterance from SmoothTalker's prosody rules — but there is no knob for it.

## Limitations

- **Limited rate range.** The engine's fastest setting is only about 1.45× its
  default speed, far slower than experienced screen reader users often prefer.
  That is a limit of the 1990 engine, not of the add-on.
- One voice: SmoothTalker 3.5, male.
- The engine accepts at most 255 characters per call — its length field is a
  single byte. Longer text is split at sentence boundaries (falling back to
  clause, then word breaks) and spoken as consecutive utterances, so nothing is
  lost, but a long unbroken sentence may have a slight pause where it was
  divided, because the engine restarts its prosody at each break.

## Layout

    manifest.ini                                add-on manifest
    installTasks.py                             config cleanup on install
    doc/en/readme.html                          the add-on's bundled help
    build.py                                    packages the .nvda-addon
    synthDrivers/smoothtalker.py                the NVDA driver
    synthDrivers/_smoothtalker_engine/core.py   the emulation core
    synthDrivers/_smoothtalker_engine/engine.bin  engine memory image
    synthDrivers/_smoothtalker_engine/lib/       bundled Unicorn 2.1.4 (x64)

The engine package name starts with an underscore on purpose: NVDA scans
`synthDrivers/` for synthesizers and skips names beginning with `_`.

## Build

    python build.py

Produces `sbaitso-<version>.nvda-addon` in the repository root, reading the
version from `manifest.ini`.

## Copyright and licensing

The add-on code is licensed under the **MIT License** — see [LICENSE](LICENSE).
Unicorn, bundled in `synthDrivers/_smoothtalker_engine/lib/`, is not covered by it:
it is GPL-2.0, and its licence text is in [NOTICE.md](NOTICE.md).

**The bundled engine image is not mine to license.** SmoothTalker is
© 1983–1990 First Byte. The two patents it was originally covered by
(U.S. 4,692,941 and 4,617,645) have long since expired, but the engine code and
voice data in `engine.bin` remain under copyright, and that file is derived from
an original Creative Labs distribution. It is included here so the add-on works
out of the box; be aware that this is redistribution of copyrighted material and
that a rights holder could ask GitHub to take it down. If you would rather not
rely on the bundled copy, delete `engine.bin` and supply your own, captured from
your own copy of Dr. Sbaitso.

## Credits

Add-on by Josh Kennedy &lt;joshknnd1982@gmail.com&gt;.

The engine interface — `INT 2Fh AX=0FBFBh` returning `ES:BX`, the far entry
point at `[ES:BX+4]`, the text buffer at `ES:BX+20h` with its leading length
byte, and the settings block at `buffer+0x200` — was recovered by reverse
engineering the original binaries. The field names used throughout the source
(`gender, tone, volume, pitch, speed, startpos, action`) are First Byte's own:
`READ.EXE` and `SET-ECHO.EXE` both embed the structure's field list.
