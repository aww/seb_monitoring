Sebastian's monitoring scripts
==============

I use this script to make plots of my son Sebastian's weight, height, and head circumference,
comparing this data to standards (included data files from the WHO).
The output is seb_monitoring.png with three plots stacked vertically.

The data is private, stored in a Google Doc and cached in sebastians_growth.pickle.
If sebastian_growth.pickle does not exist then a prompt asks for my password to download and create this file.
