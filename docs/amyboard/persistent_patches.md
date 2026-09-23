# Persistent accessory patches (surviving a sketch.py swap)

`/user/current/sketch.py` is managed by the web editor and the MIDI control
API -- downloading someone else's sketch (or sending a new one via `zT`)
overwrites it completely. Any accessory setup code you'd normally put at the
top of `sketch.py` is lost the moment a different sketch is loaded. This page
describes the alternative: a **firmware-level patch** that's applied on every
boot before the sketch runs, independent of `sketch.py`'s contents.

## Why `/boot.py` doesn't work for this

`/boot.py` (the on-filesystem, user-editable boot script) looks like the
obvious hook, but it runs too late. The real boot order (see `main.c`) is:

1. `_boot.py` (frozen) -- calls `amyboard.start_amy()`, which calls
   `run_sketch()` and executes `sketch.py`.
2. `/boot.py` (on-filesystem) -- runs *after* the sketch has already started.

So anything that needs to be in place before the sketch's top-level code
runs (e.g. `amyboard.encoder()` support for an accessory) has to hook in
earlier, inside `amyboard.start_amy()` itself.

## How it works

- `amyboard.start_amy()` (`tulip/shared/amyboard-py/amyboard.py`) calls
  `_load_user_patches()` immediately before `run_sketch()`, on both the
  normal and VCV boot paths.
- `_load_user_patches()` imports a fixed list of module names (currently just
  `modulino_encoder_patch`). Each import is wrapped in its own `try/except`, so a
  missing accessory or a broken patch can't block the sketch from booting.
- `tulip/amyboard/modules/modulino_encoder_patch.py` is **frozen into firmware**
  via `freeze(...)` in `tulip/amyboard/boards/manifest.py` -- it isn't a file on
  the `/user` filesystem, so it can't be touched by sketch uploads/downloads
  at all.
- The patch applies by import-time side effect: it wraps `amyboard.encoder`
  with a version that also detects a Modulino Knob. Because `amyboard` is a
  single cached module (`sys.modules['amyboard']`), this patched function is
  what every later `import amyboard; amyboard.encoder(...)` call sees --
  including calls from `sketch.py`, which needs no changes at all.

## Adding another persistent patch

1. Add your module to `tulip/amyboard/modules/`.
2. Freeze it in `tulip/amyboard/boards/manifest.py`:
   ```python
   freeze("$(PORT_DIR)/modules", "your_module.py")
   ```
3. Add its name to the tuple in `_load_user_patches()` in
   `tulip/shared/amyboard-py/amyboard.py`.
4. Rebuild and reflash firmware -- frozen modules only take effect after a
   new build (`idf.py -DMICROPY_BOARD=AMYBOARD build`), not a filesystem or
   sketch change.
