import random
import pygame
import pygame.midi

import time

pygame.midi.init()
port = pygame.midi.get_default_output_id()
midi_con = pygame.midi.Output(port, 0)

def sigmoid(pos): # sounds best if time based, see if that can be fixed later
	return (pos/(1-abs(pos)))

def lin_interp(start, end, size):
	diff = end-start
	step = diff/size
	final = []
	for x in range(size):
		final.append((x * step) + start)
	return final

def gen_chord(start, scale, inversion=False):
	chords = [
		[0,7],
		[0,4,7],
		[0,2,7],
		[0,5],
		[0,6],
		[0,4],
		[0,2],
		[0,2,4],
		[0,2,4,5], 
		[0,2,4,5,7],
		[0,2],
		[0,2,4],
		[0,2,4,6],
		[0,2,4,6,7]
	]

	chord = random.choice(chords)

	if inversion:
		for x in range(1, random.choice(range(len(chord)))) :
			chord[x] += 7

	chord.sort()

	fin = []

	for note in range(len(chord) ):
		fin.append(scale[chord[note] + start])

	return fin


def gen_scale(st_note, sel_sc):
	#makes scales 
	#st_note n = 0-11
	#makes list of numbers from n - 140
	#remove all numbers under 11
	#reduce all numbers by 12
	#remove all numbers over 127
	scales = {}
	scales["minor"] = [2, 1, 2, 2, 1, 2, 2]
	scales["major"] = [2, 2, 1, 2, 2, 2, 1]
	scale = []
	scale.append(st_note)

	x = 0
	cur_note = st_note
	while cur_note < 140:
		cur_note += scales[sel_sc][x%7]
		scale.append(cur_note)
		x += 1

	for x in range(12):
		if x in scale:
			scale.remove(x)
	for x in range(len(scale)):
		scale[x] -= 12
	while scale[-1] > 127:
		scale.pop()
	if len(scale) == 75:
		scale.pop()
	return scale

def gen_measure(root_notes):
	"""
	4 root notes
	gen_chord
	gen_silence(maybe)
	join all chords together
	truncate to 8 notes
	

	"""


for song in range(120):

	instrument = 1

	channel = 0 #channel 10 is index 9

	midi_con.set_instrument(instrument, channel)

	for lmnop in range(8):

		proceed = {}

		proceed["seed"] =  random.randrange(10000000)
		random.seed(proceed["seed"])
		print("%s %s" % (lmnop, proceed["seed"]))

		proceed["scale"] = random.choice(["major", "minor"])
		proceed["root"] = random.randrange(12)
		proceed["octave"] = random.randrange(3, 8)
		proceed["right"] = proceed["octave"] * 7
		proceed["left"] = 7 * random.randrange(0, proceed["octave"]-1)
		proceed["bpm"] = random.randrange(70, 200) + 120
		proceed["length"] = random.randrange(15, 50)


		volume = 127 # also give a proceedural gradient 


		scale = gen_scale( proceed["root"] , proceed["scale"])
		octave_offset = 1
		octave = proceed["octave"] + octave_offset
		separation = proceed["left"]
		note_offset = proceed["right"]
		beat_time = (60/proceed["bpm"])

		ran_notes = random.sample(range(50,500), proceed["length"] )

		root_index = []

		for note in range(len(ran_notes)-1):
			root_index.extend(lin_interp(ran_notes[note], ran_notes[note+1], 3))

		root_notes = []

		for x in root_index:
			sec_offset = 0
			root_notes.append(note_offset + sec_offset + int(sigmoid(x/1000)*10))

		#note, volume, duration	

		fin_song_low = []
		fin_song_high = []
		for note in root_notes:
			chord_high = gen_chord( note, scale )
			chord_low = gen_chord( note-separation, scale )
			if (random.choice([True, True, True, True, True, False, False])):
				broken = random.choice([True, True, True, True])
				if broken:
					for sub in chord_high:
						fin_song_high.append([sub])
					for sub in chord_low:
						fin_song_low.append([sub])
				else:
					fin_song_high.append(chord_high)
					fin_song_low.append(chord_low)
			else:
				fin_song_low.append([])
				fin_song_high.append([])

		##############add volume here########################

		song_len = len(fin_song_low)
		ran_nums = random.sample(range(50,500), 8)
		vol_index = []
		for num in range(len(ran_nums)-1):
			vol_index.extend(lin_interp(ran_nums[num], ran_nums[num+1], int(song_len/4)))
		note_vol_low =[]
		for x in vol_index:
			note_vol_low.append(60+int(sigmoid(x/1000)*60))

		song_len = len(fin_song_high)
		ran_nums = random.sample(range(50,500), 8)
		vol_index = []
		for num in range(len(ran_nums)-1):
			vol_index.extend(lin_interp(ran_nums[num], ran_nums[num+1], int(song_len/4)))
		note_vol_high =[]
		for x in vol_index:
			note_vol_high.append(60+int(sigmoid(x/1000)*60))


		#####################################################

		hit = []

		ticks = 110 #second2tick(beat_time, 480, beat_time)
		if len(fin_song_high) > len(fin_song_low):
			for x in range(len(fin_song_high)):

				for sub in fin_song_high[x] :
					if sub not in hit:

						hit.append(sub)
						midi_con.note_on(sub, note_vol_high[x] , channel)
				try:
					for sub in fin_song_low[x] :
						if sub not in hit:

							midi_con.note_on(sub, note_vol_low[x] , channel)
							hit.append(sub)
				except:
					pass

				time.sleep(beat_time)
				for sub in fin_song_high[x] :

					midi_con.note_off(sub, note_vol_high[x] , channel)
				try:
					for sub in fin_song_low[x] :

						midi_con.note_off(sub, note_vol_low[x] , channel)
				except:
					pass
				hit = []
		else:

			for x in range(len(fin_song_low)):
				try:
					for sub in fin_song_high[x] :
						if sub not in hit:
							midi_con.note_on(sub, note_vol_high[x] , channel)
							hit.append(sub)
				except:
					pass
				for sub in fin_song_low[x] :
					if sub not in hit:
						midi_con.note_on(sub, note_vol_low[x] , channel)
						hit.append(sub)
				time.sleep(beat_time)
				try:
					for sub in fin_song_high[x] :
						midi_con.note_off(sub, note_vol_high[x] , channel)
				except:
					pass
				for sub in fin_song_low[x] :
					midi_con.note_off(sub, note_vol_low[x] , channel)
				hit = []
