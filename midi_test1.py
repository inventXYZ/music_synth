import time
import board
import displayio
import terminalio
import adafruit_aw9523
import busio
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on          import NoteOn
from adafruit_midi.note_off         import NoteOff
from adafruit_midi.control_change   import ControlChange
from analogio import AnalogIn

# Read analog pin voltage for pots
def get_voltage(pin):
    return (pin.value * 3.3) / 65536

#  MIDI setup as MIDI out device
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# The potentiometers' middle pins are connected to analog pins 27 and 28, the
# outer pins to GND and 3v3.
knob_1 = AnalogIn(board.GP26)
knob_2 = AnalogIn(board.GP27)
knob_3 = AnalogIn(board.GP28)

# Use these variables to only update when the value changes
last_knob_1_val = 0
last_knob_2_val = 0
last_knob_3_val = 0

#  button pins, in order of the notes on a keyboard
note_pins = [board.GP13, board.GP11, board.GP9, board.GP7, board.GP6,
             board.GP16, board.GP14, board.GP12, board.GP10, board.GP8,
             board.GP5, board.GP4, board.GP3]

note_buttons = []

# set pin settings for piano buttons (input, pull up)
for pin in note_pins:
    note_pin = digitalio.DigitalInOut(pin)
    note_pin.direction = digitalio.Direction.INPUT
    note_pin.pull = digitalio.Pull.UP
    note_buttons.append(note_pin)
    
#midi_notes = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]
    
m = 60
    
#  note states
note0_pressed = False
note1_pressed = False
note2_pressed = False
note3_pressed = False
note4_pressed = False
note5_pressed = False
note6_pressed = False
note7_pressed = False
note8_pressed = False
note9_pressed = False
note10_pressed = False
note11_pressed = False
note12_pressed = False
note13_pressed = False
note14_pressed = False
note15_pressed = False


#  array of note states
note_states = [note0_pressed, note1_pressed, note2_pressed, note3_pressed,
               note4_pressed, note5_pressed, note6_pressed, note7_pressed,
               note8_pressed, note9_pressed, note10_pressed, note11_pressed,
               note12_pressed, note13_pressed]

up = digitalio.DigitalInOut(board.GP1)
down = digitalio.DigitalInOut(board.GP2)

octave = [up, down]

up_state = None
down_state = None

for o in octave:
    o.direction = digitalio.Direction.INPUT
    o.pull = digitalio.Pull.UP

while True:
    
    #  array of default MIDI notes
    midi_notes = [m, m + 1, m + 2, m + 3, m + 4, m + 5, m + 6, m + 7, m + 8, m + 9, m + 10, m + 11, m + 12]
    
    
    if up.value and up_state == "pressed":
        print("Up Button pressed.")
        m += 12
        up_state = None
    if down.value and down_state == "pressed":
        print("Down Button pressed.")
        m -= 12
        down_state = None 
    
    if not up.value and up_state is None:
        up_state = "pressed"
        
    if not down.value and down_state is None:
        down_state = "pressed"
            
    #  MIDI input
    for i in range(13):
        buttons = note_buttons[i]
        #  if button is pressed...
        if not buttons.value and note_states[i] is False:
            #  send the MIDI note
            midi.send(NoteOn(midi_notes[i], 120))
            note_states[i] = True
        #  if the button is released...
        if buttons.value and note_states[i] is True:
            #  stop sending the MIDI note 
            midi.send(NoteOff(midi_notes[i], 120))
            note_states[i] = False
            
    # Read voltages and convert to 0-127 (MIDI note range)
    knob_1_val = min(max(int(get_voltage(knob_1) / 3.3 * 128), 0), 127)
    knob_2_val = min(max(int(get_voltage(knob_2) / 3.3 * 128), 0), 127)
    knob_3_val = min(max(int(get_voltage(knob_3) / 3.3 * 128), 0), 127)

    # If value has changed by more than 2 since last value, send MIDI CC message
    if abs(knob_1_val - last_knob_1_val) > 2:
        midi.send(ControlChange(1, knob_1_val))
        last_knob_1_val = knob_1_val
    if abs(knob_2_val - last_knob_2_val) > 2:
        midi.send(ControlChange(2, knob_2_val))
        last_knob_2_val = knob_2_val
    if abs(knob_3_val - last_knob_3_val) > 2:
        midi.send(ControlChange(3, knob_3_val))
        last_knob_3_val = knob_3_val
