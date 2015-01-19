# -*- coding: utf-8 -*-

def drop_constraints(cursor, constraints):
	for schemaname, tablename, name, def_ in constraints:
		cursor.execute('ALTER TABLE "%s" DROP CONSTRAINT %s' % (tablename, name))

def create_constraints(cursor, constraints):
	for schemaname, tablename, name, def_ in constraints:
		cursor.execute('ALTER TABLE "%s" ADD CONSTRAINT %s %s' % (tablename, name, def_))

def all_constraints(cursor):
	cursor.execute("""
		SELECT n.nspname AS schemaname, c.relname, conname, pg_get_constraintdef(r.oid, false) as condef
			FROM  pg_constraint r, pg_class c
			LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
		WHERE 	r.contype = 'f'
				and r.conrelid=c.oid
	""")
	return cursor.fetchall()
