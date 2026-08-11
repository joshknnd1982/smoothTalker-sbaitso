# -*- coding: utf-8 -*-
"""
Clean up settings written by earlier versions of this add-on.

Versions up to 0.4.x declared rate, pitch and volume on NVDA's usual 0-100
scale.  0.5.0 switched to the engine's native 0-9 range, which makes any
stored value above 9 fail NVDA's config validation -- the synthesizer then
refuses to load at all, with "the value ... is too big".

0.6.0 also renamed the driver from "sbaitso" to "smoothtalker", so the old
section is dead weight even where the values happen to be in range.  Remove
it rather than leaving a landmine in the user's config.

The current section is left in place but clamped, for the same reason: one
out-of-range number is enough to stop the synthesizer loading, and silently
correcting it is friendlier than making the user find it in nvda.ini.
"""

from logHandler import log

OLD_SYNTH_NAMES = ('sbaitso',)
SYNTH_NAME = 'smoothtalker'
#: Ranges the driver declares in supportedSettings; keep in step with
#: synthDrivers/smoothtalker.py.
LIMITS = {'rate': (0, 9), 'pitch': (0, 9), 'volume': (0, 9), 'tone': (0, 1)}


def _purge(section, label):
    removed = []
    for name in OLD_SYNTH_NAMES:
        try:
            if name in section:
                del section[name]
                removed.append(name)
        except Exception:
            log.error('smooth talker: could not remove [%s][%s]' % (label, name),
                      exc_info=True)
    return removed


def _clamp(section, label):
    """Bring this driver's stored settings back inside their declared ranges."""
    fixed = []
    try:
        if SYNTH_NAME not in section:
            return fixed
        settings = section[SYNTH_NAME]
    except Exception:
        log.error('smooth talker: could not read [%s][%s]' % (label, SYNTH_NAME),
                  exc_info=True)
        return fixed
    for key, (low, high) in LIMITS.items():
        try:
            if key not in settings:
                continue
            value = int(settings[key])
        except Exception:
            # Not a number at all; drop it and let the default apply.
            try:
                del settings[key]
                fixed.append(key)
            except Exception:
                pass
            continue
        clamped = max(low, min(high, value))
        if clamped != value:
            try:
                settings[key] = clamped
                fixed.append(key)
            except Exception:
                log.error('smooth talker: could not clamp [%s][%s][%s]'
                          % (label, SYNTH_NAME, key), exc_info=True)
    return fixed


def onInstall():
    try:
        import config
    except Exception:
        return
    changed = []
    try:
        speech = config.conf['speech']
        changed += _purge(speech, 'speech')
        changed += _clamp(speech, 'speech')
    except Exception:
        log.error('smooth talker: could not read the speech config', exc_info=True)

    # Configuration profiles keep their own copies of the same section.
    try:
        for profile in getattr(config.conf, 'profiles', []) or []:
            try:
                if 'speech' in profile:
                    changed += _purge(profile['speech'], 'profile speech')
                    changed += _clamp(profile['speech'], 'profile speech')
            except Exception:
                pass
    except Exception:
        pass

    if changed:
        try:
            config.conf.save()
        except Exception:
            log.debugWarning('smooth talker: config save failed', exc_info=True)
        log.info('smooth talker: cleaned up stale settings for %s'
                 % ', '.join(sorted(set(changed))))
