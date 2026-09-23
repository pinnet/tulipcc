# my_amyboard.py — frozen into firmware (boards/manifest.py) and auto-imported
# by amyboard._load_user_patches() before the sketch runs, so this patch
# applies on every boot regardless of what /user/current/sketch.py contains.
#
# Adds a Modulino Knob (I2C rotary encoder accessory) as an extra device on
# amyboard.encoder(), alongside whatever encoders amyboard already detects.
# No-ops (leaves amyboard.encoder() unchanged) if no Modulino Knob is present.
import amyboard
from modulino.knob import ModulinoKnob

_i2c = amyboard.get_i2c()


class _ModulinoEncoder:
    def __init__(self, knob):
        self._knob = knob
        self._inverted = False

    def read(self, i=0):
        self._knob.update()
        pos = self._knob.value or 0
        return -pos if self._inverted else pos

    def button(self, i=0):
        self._knob.update()
        return self._knob.pressed

    def reset(self, i=0):
        self._knob.reset()

    def invert(self, on=True, i=0):
        self._inverted = on

    def led(self, i=0, r=0, g=0, b=0):
        pass  # Knob module has no onboard RGB LED


_orig_encoder = amyboard.encoder


def encoder(*args, **kwargs):
    enc = _orig_encoder(*args, **kwargs)
    try:
        # address=None auto-discovers the real bus address (0x3A or 0x3B)
        # by scanning ModulinoKnob's pinstrap default_addresses [0x74, 0x76] >> 1
        knob = ModulinoKnob(_i2c)
        knob.update()
    except Exception as e:
        print("Modulino Knob not found:", e)
        return enc

    mod = _ModulinoEncoder(knob)
    base = enc.encoders
    enc.encoders = base + 1
    enc.buttons = getattr(enc, 'buttons', base) + 1
    enc.devices = list(enc.devices) + [("modulino_knob", knob.address)]
    enc.type = "multi" if enc.type not in (None, "modulino_knob") else "modulino_knob"

    _read, _button, _reset = enc.read, enc.button, enc.reset
    _invert, _led = enc.invert, enc.led

    def read(i=0):
        return mod.read(i - base) if i >= base else _read(i)

    def button(i=0):
        return mod.button(i - base) if i >= base else _button(i)

    def reset(i=None):
        if i is None or i >= base:
            mod.reset()
        if i is None or i < base:
            _reset(i) if i is not None else _reset()

    def invert(on=True, i=None):
        if i is None or i >= base:
            mod.invert(on)
        if i is None or i < base:
            _invert(on, i) if i is not None else _invert(on)

    def led(i=0, r=0, g=0, b=0):
        mod.led(i - base, r, g, b) if i >= base else _led(i, r, g, b)

    enc.read, enc.button, enc.reset = read, button, reset
    enc.invert, enc.led = invert, led
    return enc


amyboard.encoder = encoder
from amyboard import *   