"""test download function"""
import misc
import console

OUTPUT = console.Output(True)
URL = "http://download.thinkbroadband.com/512MB.zip"
SAVEFILE = "512MB.zip"
misc.download(OUTPUT, URL, SAVEFILE, SAVEFILE)
print()
