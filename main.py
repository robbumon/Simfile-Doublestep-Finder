# STAMINA SIMFILE HELPER
# --------------------------------------------------------------------------------------
# Tracks left and right foot steps in chart to find double-steps in stamina charts
# Still has some problems with jumps and ambiguous up/down arrows


import tkinter as tk
from tkinter import filedialog
import simfile
from simfile.notes import NoteType, NoteData
from simfile.notes.group import *


def get_folder_dialog():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=(('sm files','*.sm'),('ssc fles','*.ssc')))
    return file_path


class mynote:
    def __init__(self):
        self.type = 'tap'
        self.arrow = 4
        self.foot = 2
        self.doublestep = False
        self.jack = False
        self.beat = 0


# output lists
feet = ('L', 'R', '?')
arrows = ('L', 'D', 'U', 'R', 'J')

# load simfile
file_path = get_folder_dialog()
opensimfile = simfile.open(file_path)

# begin print out
print('')
print('-------- STEP ANALYSIS --------')
print('Title: ' + opensimfile.title + ' ' + opensimfile.subtitle)
print('Artist: ' + opensimfile.artist)
print('Number of charts: ' + str(len(opensimfile.charts)))
print('--------------------------------------')

# Loop through charts in file
for chart in opensimfile.charts:
    note_data = NoteData(chart)

    print(chart.difficulty + ' ' + str(chart.meter) + ' : ' + chart.description)

    # -------------------------------------
    # BREAKDOWN BUDDY LITE
    # -------------------------------------
    breakdown_data = NoteData(chart)
    breakdown_iterator = group_notes(
        breakdown_data,
        same_beat_notes=SameBeatNotes.JOIN_BY_NOTE_TYPE,
        include_note_types={NoteType.HOLD_HEAD, NoteType.TAIL, NoteType.TAP},
        join_heads_to_tails=True,
        orphaned_tail=OrphanedNotes.DROP_ORPHAN,
    )

    # parse notes for streams
    prevbeat = 0
    streamstart = 0
    streamend = 0
    streamcount = 0
    instream = False
    breakdown = [[1, 0, 0, 0]]
    for note in breakdown_iterator:
        if (note[0].beat - prevbeat) <= 0.25:
            streamcount += 1
            if not instream:
                instream = True
                streamstart = note[0].beat
        else:
            if instream:
                streamend = note[0].beat
                breakdown.append([1, streamstart, streamend, streamcount])
                streamcount = 0
                instream = False
        #print(str(note[0].beat) + ' - ' + str(instream) + ' - ' + str(prevbeat) + ' - ' + str(breakdown))
        prevbeat = note[0].beat

    # end of file in stream
    if instream:
        breakdown.append([1, streamstart, streamend, streamcount])

    # remove streams < 16 notes long
    finalbreakdown = [[1, 0, 0, 0]]
    for s in breakdown:
        if s[3] >= 16:
            finalbreakdown.append(s)

    # subtract stream start from prev stream end to get break
    bd = 'Full Breakdown: '
    prevend = 0
    for s in finalbreakdown:
        b = s[1] - prevend
        if (b/16) >= 1:
            bd = bd + '(' + str(round(b/16)) + ')' + ' '
        if s[3] > 0:
            bd = bd + str(round(s[3]/16)) + ' '
        prevend = s[2]
    print(bd)


    # -------------------------------------
    # DOUBLE-STEP FINDER
    # -------------------------------------
    currentnote = mynote()
    prevnote = mynote()

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
        if (prevnote.arrow == 4) or ((currentnote.beat - prevnote.beat) > 2):
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
            print('Doublestep at beat:' + str(note[0].beat) + ' arrow:' + arrows[currentnote.arrow] + ' foot:' + feet[currentnote.foot])

    print('--------------------------------------')


