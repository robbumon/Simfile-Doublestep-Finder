# Simfile-Doublestep-Finder
Specifically for stamina charts, this looks for accidental doublesteps created in streams/breaks.

Note: I use the library simfile for Python 3 which is absolutely awesome to work with.

https://simfile.readthedocs.io/en/latest/index.html

`pip3 install simfile` 

When you play the latest version of Simply Love, each chart comes with a handy "crossovers" and "footswitch" counter.
This is helpful to determine if your stamina chart, which traditionally will never have these patterns, has these mistakes.

So I was tired of looking through a marathon chart for accidental doublesteps and I created this little script to track each step for each foot. 

It's not perfect and gets hung up on some jump sections. In fact, if there are jumps in the break, I count them as "ambiguous" and following steps can't be marked as doublesteps. I think that's fair.

To do:
 - Add step statistics for stamina breakdown
 - Reinvent the wheel a third time
