# my_amyboard.py — drop into /user/current/
import amyboard
from modulino import Knob

_MOD_ADDR = 0x76

class _ModulinoEncoder:
    """Wraps a Modulino Knob to match the amyboard Encoder API."""
    def __init__(self, knob):
        self._knob = knob
        self._inverted = False
        self.type = "modulino_knob"
        self.devices = [("modulino_knob", _MOD_ADDR)]
        self.encoders = 1
        self.buttons = 1
        self.leds = 0

    def read(self, i=0):
        pos = self._knob.get()
        return -pos if self._inverted else pos

    def button(self, i=0):
        return self._knob.is_pressed()

    def reset(self, i=None):
        self._knob.set(0)

    def invert(self, on=True, i=None):
        self._inverted = on

    def led(self, i=0, r=0, g=0, b=0):
        pass

    def switch(self):
        return False

# Patch amyboard.encoder to include the Modulino
_orig_encoder = amyboard.encoder

def encoder(*args, **kwargs):
    enc = _orig_encoder(*args, **kwargs)
    # Try to detect a Modulino Knob
    try:
        knob = Knob(addr=_MOD_ADDR)
        knob.get()  # sanity check
        mod_enc = _ModulinoEncoder(knob)
        # Merge: offset modulino after existing encoders
        base = enc.encoders
        enc.encoders = base + 1
        enc.buttons = getattr(enc, 'buttons', base) + 1
        enc.devices = list(enc.devices) + mod_enc.devices
        if enc.type is None:
            enc.type = "modulino_knob"
        elif enc.type != "multi":
            enc.type = "multi"
        _base_read = enc.read
        _base_button = enc.button
        _base_reset = enc.reset
        def read(i):
            if i >= base:
                return mod_enc.read(i - base)
            return _base_read(i)
        def button(i):
            if i >= base:
                return mod_enc.button(i - base)
            return _base_button(i)
        def reset(i=None):
            if i is None:
                _base_reset()
                mod_enc.reset()
            elif i >= base:
                mod_enc.reset()
            else:
                _base_reset(i)
        enc.read = read
        enc.button = button
        enc.reset = reset
    except (OSError, ValueError, ImportError):
        pass  # No Modulino present
    return enc

amyboard.encoder = encoder

# Re-export everything so `import my_amyboard` works like `import amyboard`
from amyboard import *   