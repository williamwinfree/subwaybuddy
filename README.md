# subwaybud


# Initial Setup & Hardware

-Raspberry Pi Zero to 4 (RGB Matrix Library not currently compatible with RasPi 5); best results when run headless

-64x32 RGB LED Matrix:

-Adafruit RGB LED Matrix Hat/Matrix Bonnet & Power Supply:



## Packages to install

	sudo apt-get install git
	sudo apt-get install libavformat-dev
	sudo apt-get install graphicsmagick-libmagick-dev-compat
	sudo apt-get install libswscale-dev
	sudo apt install python3-pip
	sudo pip3 install schedule --break-system-packages
	sudo pip3 install gtfs-realtime-bindings --break-system-packages
	sudo pip3 install protobuf-to-dict --break-system-packages
	sudo pip3 install pandas --break-system-packages
	sudo pip3 install pillow --break-system-packages

A note on protobuf-to-dict if using Python3: several lines have deprecated references and need to be changed. Open protobuf-to-dict.py in your site packages folder and between lines 12-27 change all "long" to "int" and change "unicode" on line 25 to "str".


## Selecting Your Station:

Open the "stopcrosswalk.csv" file and add an "x" in the left-most column next to the station you would like the matrix to display. It is defaulted to Jay Street Metrotech, so make sure you remove the "x" next to this stop before saving. Some stations have more than one train group that go through them (e.g. Jay Street Metrotech). You can select up to 4 different train groups per station.

You can adjust the time cutoff for trains in both the mta.py and/or the mta_no_matrix.py files. The lower bound "walk" will prevent the tracker from showing trains coming sooner than the value you enter and the upperbound "cutoff" excludes trains above the value you enter.


# Test the Tracker:

At this point, you can run the mta_no_matrix.py script to make sure that the program is functioning correctly. You can run directly in the terminal from your "subwaybud" folder using:

	sudo python3 mta_no_matrix.py

You should see the station name that you selected in the crosswalk and a list of upcoming uptown and downtown trains in the terminal.



# Updating RPI RGB LED Matrix Lib

	curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh >rgb-matrix.sh

	sudo bash rgb-matrix.sh
	
Select: Adafruit Bonnet or AdaFruit Hat w/ RTC

Select: Convenience or Quality (Quality if Soldered)


In /rpi-rgb-led-matrix:
	
	-make all

In /rpi-rgb-led-matrix/utils:
	
 	-make all

# Text Scroller Test: Make Sure Matrix is Working

in /rpi-rgb-led-matrix/utils:

	sudo ./text-scroller -f ../fonts/9x18.bdf -C255,0,0 --led-rows=32 --led-cols=64 --led-gpio-mapping=adafruit-hat --led-pixel-mapper="Rotate:180" "Hi Mom"

Be sure to update parameters as relevant to your setup (e.g. hat vs bonnet). Some tinkering may be required. See rpi-rgb-led-matrix respository for more examples and techniques to improve image.


# Run the Program!

Intiate the script with 

	sudo python3 mta.py

The splash screen should load and the tracker will display after. Hooray! Now the tracker will refresh every 1 minute in sync with the train crawl across the top.


## Helpful Links:
https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi/driving-matrices

https://github.com/hzeller/rpi-rgb-led-matrix
