# Just not _boot, we have our own
freeze("$(PORT_DIR)/modules", "apa106.py")
freeze("$(PORT_DIR)/modules", "inisetup.py")
freeze("$(PORT_DIR)/modules", "espnow.py")
freeze("$(PORT_DIR)/modules", "flashbdev.py")
# User accessory patch (Modulino Knob encoder support), auto-loaded by
# amyboard.start_amy() before the sketch runs -- see _load_user_patches()
# in shared/amyboard-py/amyboard.py. Frozen (not in /user/current) so it
# survives downloading a different sketch.py from the web editor.
freeze("$(PORT_DIR)/modules", "my_amyboard.py")

include("$(MPY_DIR)/extmod/asyncio")

# Useful networking-related packages.
#require("mip")
require("ntptime")
require("webrepl")  # WebREPL server (REPL over WiFi); _webrepl C module is enabled in mpconfigport.h

# Require some micropython-lib modules.
# require("aioespnow")
require("dht")
require("ds18x20")
require("onewire")
require("umqtt.robust")
require("umqtt.simple")

freeze("$(PORT_DIR)/../shared/py")
freeze("$(PORT_DIR)/../shared/amyboard-py")
package("amy", base_path="$(MPY_DIR)/../amy")

#freeze("$(MPY_DIR)/lib/micropython-lib/micropython/utarfile", "utarfile.py")
