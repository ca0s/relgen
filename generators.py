# -*- coding: utf-8 -*-

from random import randint, setstate, getstate, seed
import datetime

def gen_previous(previous, s, tr, unique=False, filt=None):
	o = getstate()
	seed(s)
	my_state = getstate()
	setstate(o)
	i = 0
	while True:
		o = getstate()
		setstate(my_state)
		#r = str(previous[randint(0, len(previous)-1)])
		r = str(previous[i%len(previous)])
		i = i+1
		done = False
		while not done:
			done = True
			if unique and r in tr:
				done = False
			if filt != None and not filt(r):
				done = False
			if not done:
				#r = str(previous[randint(0, len(previous)-1)])
				r = str(previous[i%len(previous)])
				i = i+1
		if tr != None:
			tr.append(r)
		my_state = getstate()
		setstate(o)
		yield r

def gen_inc_int(prefix, suffix, prev=None, unique=False):
	i = 0
	while True:
		ii = prefix + str(i) + suffix
		if unique:
			while ii in prev:
				ii = prefix + str(i) + suffix
		if prev != None:
			prev.append(ii)
		yield ii
		i = i+1
		
def gen_randstr(prefix, suffix, charset, l, prev=None, unique=False):
	while True:
		s = prefix + ''.join(charset[randint(0, len(charset)-1)] for i in range(l)) + suffix
		if unique:
			while s in prev:
				s = prefix + ''.join(charset[randint(0, len(charset)-1)] for i in range(l)) + suffix
		if prev != None:
			prev.append(s)
		yield s

def gen_randint(prefix, suffix, begin, end, prev=None, unique=False):
	while True:
		n = prefix + str(randint(begin, end)) + suffix
		if unique:
			while n in prev:
				n = prefix + str(randint(begin, end)) + suffix
		if prev != None:
			prev.append(n)
		yield n
		
def gen_randchoose(prefix, suffix, values, prev=None, unique=False):
	while True:
		c = values[randint(0, len(values) - 1)]
		if unique:
			while c in prev:
				c = values[randint(0, len(values) - 1)]
		if prev != None:
			prev.append(c)
		yield values[randint(0, len(values) - 1)]

def gen_randdate(prefix, suffix, begin, end, prev=None, unique=False):
	b = begin.split('/')
	e = end.split('/')
	btime = datetime.date.toordinal(datetime.date(int(b[2]), int(b[1]), int(b[0])))
	etime = datetime.date.toordinal(datetime.date(int(e[2]), int(e[1]), int(e[0])))
	while True:
		delta = randint(0, etime - btime)
		d = prefix + datetime.date.fromordinal(btime + delta).strftime('%d/%m/%Y') + suffix
		if unique:
			while d in prev:
				delta = randint(0, etime - btime)
				d = prefix + datetime.date.fromordinal(btime + delta).strftime('%d/%m/%Y') + suffix
		if prev != None:
			prev.append(d)
		yield d
		
def gen_incdate(prefix, suffix, begin, end, prev=None, unique=False):
	b = begin.split('/')
	e = end.split('/')
	btime = datetime.date.toordinal(datetime.date(int(b[2]), int(b[1]), int(b[0])))
	etime = datetime.date.toordinal(datetime.date(int(e[2]), int(e[1]), int(e[0])))
	c = btime
	while True:
		d = prefix + datetime.date.fromordinal(c).strftime('%d/%m/%Y') + suffix
		c = c + 1
		if c > etime:
			c = btime
		if prev != None:
			prev.append(d)
		yield d			

def gen_randtime(prefix, suffix, begin, end, key=False, prev=False, unique=False):
	b = begin.split(':')
	e = end.split(':')
	btime = int(b[0]) * 60 + int(b[1])
	etime = int(e[0]) * 60 + int(e[1])
	while True:
		delta = randint(btime, etime-btime)
		ntime = btime + delta
		t = prefix + str(ntime / 60) + ':' + str(ntime % 60) + suffix
		if unique:
			while t in prev:
				delta = randint(btime, etime-btime)
				ntime = btime + delta
				t = prefix + str(ntime / 60) + ':' + str(ntime % 60) + suffix
		if prev != None:
			prev.append(t)
		yield t

def gen_inctime(prefix, suffix, begin, end, key=False, prev=False, unique=False):
	b = begin.split(':')
	e = end.split(':')
	btime = int(b[0]) * 60 + int(b[1])
	etime = int(e[0]) * 60 + int(e[1])
	ntime = btime
	while True:
		t = prefix + str(ntime / 60) + ':' + str(ntime % 60) + suffix
		ntime = ntime + 1
		if ntime > etime:
			ntime = btime
		if prev != None:
			prev.append(t)
		yield t
