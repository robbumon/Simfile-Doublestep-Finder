# SIMFILE DOUBLESTEP FINDER
# --------------------------------------------------------------------------------------
# Tracks left and right foot steps in chart to find double-steps in stamina charts
# Still has problems with jumps and ambiguous up/down arrows
#
# TODO:
#   More granular with jump and foot landing


import simfile
from simfile.notes import NoteType, NoteData
from simfile.timing import Beat
from simfile.notes.group import *
from simfile.notes.count import *

feet = ('L', 'R', '?')
arrows = ('L', 'D', 'U', 'R', 'J')

class mynote:
    def __init__(self, type, arrow, foot, doublestep, jack, beat):
        self.type = type
        self.arrow = arrow
        self.foot = foot
        self.doublestep = doublestep
        self.jack = jack
        self.beat = beat


currentnote = mynote('tap', 4, 2, False, False, 0)
prevnote = mynote('tap', 4, 2, False, False, 0)

# load simfile
# opensimfile = simfile.open('/Users/rfnic/Documents/ArrowVortex 2017-02-25/Songs/WIP/Fly Me To The Moon/Fly Me To The Moon 156.sm')
opensimfile = simfile.open('/Users/rfnic/Documents/ArrowVortex 2017-02-25/Songs/Sick Music Pending/Sick Music for Stamina - Full/Sick Music for Stamina - Full mix.sm')
chart = opensimfile.charts[0]
note_data = NoteData(chart)


# Get note data with jumps grouped together
note_data = NoteData(chart)
group_iterator = group_notes(
    note_data,
    same_beat_notes=SameBeatNotes.JOIN_BY_NOTE_TYPE,
    include_note_types={NoteType.HOLD_HEAD, NoteType.TAIL, NoteType.TAP},
    join_heads_to_tails=True,
    orphaned_tail=OrphanedNotes.DROP_ORPHAN,
)

# Loop through note data
for note in group_iterator:
    currentnote.jack = False
    currentnote.doublestep = False
    currentnote.jump = False
    currentnote.beat = note[0].beat

    # find jumps
    if len(note) > 1:
        currentnote.type = 'jump'
        currentnote.arrow = 4
    else:
        currentnote.type = 'tap'
        currentnote.arrow = note[0].column

    # previous jump note or > 1 beat between notes, then no double-steps
    if (prevnote.type == 'jump') or ((currentnote.beat - prevnote.beat) > 1):
        currentnote.foot = 2
        #if currentnote.arrow == 0:
        #    currentnote.foot = 0
        #elif currentnote.arrow == 3:
        #    currentnote.foot = 1
        #else:
        #    currentnote.foot = 2

    # previous tap note
    else:
        # first note
        if prevnote.foot == 2:
            if currentnote.arrow == 0:
                currentnote.foot = 0
            elif currentnote.arrow == 3:
                currentnote.foot = 1
            else:
                currentnote.foot = 2

        # right, but previous was up and right foot
        elif prevnote.arrow == 2 and prevnote.foot == 1 and note[0].column == 3 and currentnote.arrow != 4:
            currentnote.doublestep = True
            currentnote.foot = prevnote.foot

        # right, but previous was down and right foot
        elif prevnote.arrow == 1 and prevnote.foot == 1 and note[0].column == 3 and currentnote.arrow != 4:
            currentnote.doublestep = True
            currentnote.foot = prevnote.foot

        # left, but previous was up and left foot
        elif prevnote.arrow == 2 and prevnote.foot == 0 and note[0].column == 0 and currentnote.arrow != 4:
            currentnote.doublestep = True
            currentnote.foot = prevnote.foot

        # left, but previous was down and left foot
        elif prevnote.arrow == 1 and prevnote.foot == 0 and note[0].column == 0 and currentnote.arrow != 4:
            currentnote.doublestep = True
            currentnote.foot = prevnote.foot

        # jack
        elif prevnote.arrow == note[0].column:
            currentnote.jack = True
            currentnote.foot = prevnote.foot

        # all else alternate feet
        else:
            if prevnote.foot == 0:
                currentnote.foot = 1
            else:
               currentnote.foot = 0

    # capture previous note information
    prevnote.foot = currentnote.foot
    prevnote.arrow = note[0].column
    prevnote.type = currentnote.type
    prevnote.beat = currentnote.beat

    # print doublestep results
    if currentnote.doublestep:
        print('beat:' + str(note[0].beat) + ' arrow:' + arrows[currentnote.arrow] + ' foot:' + feet[currentnote.foot] + ' double?' + str(currentnote.doublestep))


