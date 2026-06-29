# dmgbuild settings for Ice. Invoked by the release workflow:
#   dmgbuild -s Scripts/dmg-settings.py -D app=... -D background=... "Ice" out.dmg
#
# dmgbuild writes the .DS_Store directly (no Finder/AppleScript), so the styled
# install window renders reliably on headless CI — unlike create-dmg, whose
# Finder-scripted layout fails on CI runners. Icon positions and the 600x430
# window match Scripts/make-dmg-bg.py (the background is 600x400; the window must
# be ~430 tall so the title bar doesn't push the content into a scrollbar).
import os.path

app = defines.get("app", "Ice.app")
appname = os.path.basename(app)

files = [app]
symlinks = {"Applications": "/Applications"}
hide_extensions = [appname]

format = "UDZO"

background = defines.get("background", "Scripts/dmg-background.tiff")
window_rect = ((200, 150), (600, 430))
icon_size = 128
icon_locations = {
    appname: (150, 235),
    "Applications": (450, 235),
}
