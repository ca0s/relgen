# -*- coding: utf-8 -*-
'''
relgen.py
by @ca0s_
ca0s@ka0labs.net
'''
from random import randint
from sys import maxint, stderr, argv
import time
import MySQLdb
import psycopg2
import json
import generators
import filters
import constraints

full_charset = 'abcdefghijklmnopqrstuvwxyz0123456789'

def allfields(fields):
	return ', '.join([field['name'] for field in fields])
	
def allvalues(fields):
	return ', '.join(["'" + field['generator'].next() + "'" for field in fields])
	
def getrelation(relations, name):
	for relation in relations:
		if relation['name'] == name:
			return relation
	return None
	
def getfield(relation, name):
	for field in relation['fields']:
		if field['name'] == name:
			return field
	return None
	
def parse_args(argv):
	args = {
		'sql': {
			'host': '127.0.0.1',
			'port': '',
			'user': '',
			'pass': '',
			'db': '',
			'noinsert': False
			}
	}
	l = len(argv)
	for i in range(l):
		if argv[i] == '-h':
			args['help'] = True
		elif argv[i] == '-sdel':
			args['sql']['del'] = True
		elif argv[i] == '-sni':
			args['sql']['noinsert'] = True
		elif argv[i] == '-snri':
			args['sql']['nri'] = True
		if i < l:
			if argv[i] == '-sgbd':
				if argv[i+1] in ['mysql', 'postgresql']:
					args['sql']['sgbd'] = argv[i+1]
			elif argv[i] == '-shost':
				args['sql']['host'] = argv[i+1]
			elif argv[i] == ['-sport']:
				args['sql']['port'] = argv[i+1]
			elif argv[i] == '-suser':
				args['sql']['user'] = argv[i+1]
			elif argv[i] == '-spass':
				args['sql']['pass'] = argv[i+1]
			elif argv[i] == '-sdb':
				args['sql']['db'] = argv[i+1]
			elif argv[i] == '-f':
				args['datafile'] = argv[i+1]
	return args

if __name__ == '__main__':
	con = None
	args = parse_args(argv)
	if 'help' in args or 'datafile' not in args:
		print >> stderr, 'python2 relgen.py [-h] -f data_definition.rel [-sgbd {mysql|postgresql} -sdb sql_database [-shost sql_host [-sport sql_port]] [-suser sql_user [-spass sql_pass]] [-sdel]]'
		print >> stderr, '\t-h\t\t\t\tShow this help'
		print >> stderr, '\t-f\t\t\t\tFile to load data definition from'
		print >> stderr, '\t-sgbd (optional)\t\tInsert data in a database of given type. MySQL and PostgreSQL are supported'
		print >> stderr, '\t\t-sdb\t\t\tDatabase to use'
		print >> stderr, '\t\t-shost (optional)\tHost of the SQL server'
		print >> stderr, '\t\t-sport (optional)\tPort of the SQL server'
		print >> stderr, '\t\t-suser (optional)\tSQL user to use'
		print >> stderr, '\t\t\t-spass (optional) SQL password to use'
		print >> stderr, '\t\t-sdel (optional)\tDelete all rows from table before insert'
		print >> stderr, '\t\t-snri (optional)\tDisable referetial integrity'
		print >> stderr, '\t\t-sni	(optional)\tDo not execute any INSERT query (useful with -sdel)'
		exit(0)
	try:
		fd = open(args['datafile'], 'r')
	except:
		print >> stderr, '[-] Error: cannot open file'
		exit(-1)
	try:
		my_relations = json.load(fd)
	except:
		print >> stderr, '[-] Error: invalid JSON'
		exit(-1)
	fd.close()
	print >> stderr, '[+] Data definition loaded'
	
	if 'sgbd' in args['sql']:
		print >> stderr, '[/] Connecting to database...'
		try:
			if args['sql']['sgbd'] == 'mysql':
				con = MySQLdb.connect(host=args['sql']['host'], port=args['sql']['port'],
										user=args['sql']['user'], passwd=args['sql']['pass'],
										db=args['sql']['db'])
			elif args['sql']['sgbd'] == 'postgresql':
				con = psycopg2.connect(host=args['sql']['host'], port=args['sql']['port'],
										user=args['sql']['user'], password=args['sql']['pass'],
										database=args['sql']['db'])
			cursor = con.cursor()
		except Exception as e:
			print >> stderr, '\terror', e
			exit(-1)
		print >> stderr, '\tconnected'
		cursor.execute('SET datestyle = ISO, DMY;')
		if args['sql'].get('nri', False):
			print >> stderr, '[+] Disabling referential integrity...'
			try:
				my_constraints = constraints.all_constraints(cursor)
				constraints.drop_constraints(cursor, my_constraints)
			except Exception as e:
				print >> stderr, '\terror', e
				exit(-1)

	relations = []
	dependants = []
	
	# Comprobar relaciones
	print >> stderr, '[/] Checking data definition...'
	for relation in my_relations:
		depends = False
		for field in relation['fields']:
			references = field.get('references', None)
			if references:
				for reference in references:
					(relname, relfield) = reference.split('.')
					refrel = getrelation(my_relations, relname)
					if refrel:
						reffield = getfield(refrel, relfield)
						if reffield:
							reffield['referenced'] = True
						else:
							print >> '\terror:', stderr, relation['name'] + '.' + field['name'] + ' references an inexistant field (' + relfield + ')'
							exit()
					else:
						print >> '\terror:', stderr, relation['name'] + '.' + field['name'] + ' references an inexistant relation (' + relname + ')'
						exit()
				depends = True
		if not depends:
			relations.append(relation)
		else:
			dependants.append(relation)

	if len(relations) == 0:
		print >> stderr, '\terror: you must provide at least one independent relation'
		exit()
	print >> stderr, '\tOK'

	# Reordenar relaciones para cumplir dependencias al generar
	print >> stderr, '[/] Sorting relations...'
	while len(dependants) > 0:
		n = len(dependants)
		for i in range(n):
			satisfied = True
			for f in dependants[i]['fields']:
				if 'references' in f:
					for r in f['references']:
						if getrelation(relations, r.split('.')[0]) == None:
							satisfied = False
							break
					if not satisfied:
						break
			if satisfied:
				relations.append(dependants[i])
				dependants.pop(i)
				break
	print >> stderr, '\tdone'

	# Inicializar generadores
	print >> stderr, '[/] Initializing data generators...'
	for relation in relations:
		s = randint(0, maxint)
		for field in relation['fields']:
			refered = field.get('referenced', False)
			unique = field.get('unique', False)
			if refered or unique:
				prev = []
				field['prev'] = prev
			else: 
				prev = None
				
			if 'references' in field:
				(rel, f) = field['references'][0].split('.')
				refered_field = getfield(getrelation(relations, rel), f)
				#print relation['name'], '.', field['name'], 'references',rel, '.', f, refered_field
				p = field.get('filter', None)
				if p != None:
					field['generator'] = generators.gen_previous(refered_field['prev'], s, prev, unique=unique, filt=filters.filters[p])
				else:
					field['generator'] = generators.gen_previous(refered_field['prev'], s, prev, unique=unique)
			else:
				gentype = field.get('gentype', 'inc_int')
				if gentype == 'inc_int':
					field['generator'] = generators.gen_inc_int(field.get('prefix', ''), field.get('suffix', ''),
													prev = prev, unique=unique)
				elif gentype == 'randstr':
					field['generator'] = generators.gen_randstr(field.get('prefix', ''), field.get('suffix', ''), 
													field.get('charset', full_charset), field.get('genlen', 10),
													prev = prev, unique=unique)
				elif gentype == 'randdate':
					field['generator'] = generators.gen_randdate(field.get('prefix', ''), field.get('suffix', ''),
													field.get('genbegin', '1/1/2010'), field.get('genend', '32/12/2010'),
													prev = prev, unique=unique)
				elif gentype == 'inc_date':
					field['generator'] = generators.gen_randdate(field.get('prefix', ''), field.get('suffix', ''),
													field.get('genbegin', '1/1/2010'), field.get('genend', '32/12/2010'),
													prev = prev, unique=unique)
				elif gentype == 'randtime':
					field['generator'] = generators.gen_randtime(field.get('prefix', ''), field.get('suffix', ''),
													field.get('genbegin', '00:00'), field.get('genend', '23:59'),
													prev = prev, unique=unique)
				elif gentype == 'inc_time':
					field['generator'] = generators.gen_inctime(field.get('prefix', ''), field.get('suffix', ''),
													field.get('genbegin', '00:00'), field.get('genend', '23:59'),
													prev = prev, unique=unique)
				elif gentype == 'randint':
					field['generator'] = generators.gen_randint(field.get('prefix', ''), field.get('suffix', ''),
													field.get('genbegin', 0), field.get('genend', 9001),
													prev = prev, unique=unique)
				elif gentype == 'randchoose' and 'values' in field:
					field['generator'] = generators.gen_randchoose(field.get('prefix', ''), field.get('suffix', ''),
													field['values'],
													prev = prev, unique=unique)
	print >> stderr, '\tdone'
		
	# Delete?
	if con != None and args['sql'].get('del', False):
		print >> stderr, '[/] Deleting from all tables...'
		for r in reversed(relations):
			print >> stderr, '\t' + r['name']
			query = 'DELETE FROM ' + r['name'] + ';'
			cursor.execute(query)	
			
	if args['sql']['noinsert'] == False:
		# Generar datos
		print >> stderr, '[/] Generating data...'
		if con:
			cursor.execute('SAVEPOINT sp;')
		for relation in relations:
			prev_progress = 0
			errors = 0
			start = time.time()
			for i in range(relation['n']):
				progress = (float(i) / relation['n'])*100
				progress_i = int(progress)
				progress_f = round(progress, 2)
				done = int(progress_i / 10) + 1
				if progress_f != prev_progress:
					prev_progress = progress_f
					stderr.write('\r\trelation \'' + relation['name'] + '\'\t[{0}{1}] {2}%'.format('#'*done, ' '*(10-done), progress_f))
					stderr.flush()
				query = 'INSERT INTO ' + relation['name'] + ' (' + allfields(relation['fields']) + ') VALUES (' + allvalues(relation['fields']) + ');'
				if con != None:
					success = False
					while not success:
						try:
							cursor.execute(query)
							#cursor.execute('RELEASE sp;')
							#cursor.execute('SAVEPOINT sp;')
							con.commit() ########################### REMOVE MEE!!!!!
							success = True
						except Exception as e:
							errors = errors + 1
							#cursor.execute('ROLLBACK TO SAVEPOINT sp;')
							query = 'INSERT INTO ' + relation['name'] + ' (' + allfields(relation['fields']) + ') VALUES (' + allvalues(relation['fields']) + ');'
				else:
					print query
			print >> stderr, ''
			print >> stderr, '\t\t' + str(errors) + ' errors'
			end = time.time()
			print >> stderr, '\t\ttime: ' + str(end-start) + ' seconds'

	if con:
		if args['sql'].get('nri', False):
			constraints.create_constraints(cursor, my_constraints)
		con.commit()
		cursor.close()
		con.close()
	
	print >> stderr, '[+] Done. Enjoy your shit-filled database :)'
