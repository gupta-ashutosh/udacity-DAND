import sqlite3
import pandas as pd

database = "newdelhi_ncr_osm.db"
conn = ''
def create_connection(db_file):
	""" creating connection with SQLITE3"""
	try:
		conn = sqlite3.connect(db_file)
		conn.text_factory = str
		return conn
	except Exception as e:
		print(e)

	return None

def create_table(conn, create_table_sql):
	""" get the connection object and create tables"""
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except Exception as e:
		print e


def main():
	""" structure for table, schema"""

	sql_create_nodes = """CREATE TABLE IF NOT EXISTS nodes (
		    id INT PRIMARY KEY NOT NULL,
		    lat REAL,
		    lon REAL,
		    user TEXT,
		    uid INT,
		    version TEXT,
		    changeset INT,
		    timestamp TEXT
		);"""
	
	sql_create_nodes_tags = """ CREATE TABLE IF NOT EXISTS nodes_tags (
		    id INT,
		    key TEXT,
		    value TEXT,
		    type TEXT,
		    FOREIGN KEY (id) REFERENCES nodes(id)
		);"""

	sql_create_ways_table = """ CREATE TABLE IF NOT EXISTS ways (
		    id INT PRIMARY KEY NOT NULL,
		    user TEXT,
		    uid INTEGER,
		    version TEXT,
		    changeset INTEGER,
		    timestamp TEXT
		);"""

	sql_create_ways_tags = """ CREATE TABLE IF NOT EXISTS ways_tags (
		    id INTEGER NOT NULL,
		    key TEXT NOT NULL,
		    value TEXT NOT NULL,
		    type TEXT,
		    FOREIGN KEY (id) REFERENCES ways(id)
		);"""

	sql_create_ways_nodes = """ CREATE TABLE IF NOT EXISTS ways_nodes (
		    id INTEGER NOT NULL,
		    node_id INTEGER NOT NULL,
		    position INTEGER NOT NULL,
		    FOREIGN KEY (id) REFERENCES ways(id),
		    FOREIGN KEY (node_id) REFERENCES nodes(id)
		);"""


	conn = create_connection(database)
	if conn is not None:
		"""create nodes table """
		create_table(conn, sql_create_nodes)

		""" create nodes_tags table """
		create_table(conn, sql_create_nodes_tags)

		""" create ways table """
		create_table(conn, sql_create_ways_table)

		""" create ways_tags table """
		create_table(conn, sql_create_ways_tags)

		""" create ways_nodes table """
		create_table(conn, sql_create_ways_nodes)
	else:
		print "error can not create connection!!"

def insert_data():
	""" inserting csv files into respective tables"""

	""" connection object """
	conn = create_connection(database)

	if conn is not None:
		""" importing nodes.csv to nodes table """
		df = pd.read_csv("nodes.csv")
		df.to_sql("nodes", conn, if_exists='replace', index=False)

		""" importing nodes_tags.csv to nodes table """
		df = pd.read_csv("nodes_tags.csv")
		df.to_sql("nodes_tags", conn, if_exists='replace', index=False)

		""" importing ways.csv to nodes table """
		df = pd.read_csv("ways.csv")
		df.to_sql("ways", conn, if_exists='replace', index=False)

		""" importing ways_tags.csv to nodes table """
		df = pd.read_csv("ways_tags.csv")
		df.to_sql("ways_tags", conn, if_exists='replace', index=False)

		""" importing ways_nodes.csv to nodes table """
		df = pd.read_csv("ways_nodes.csv")
		df.to_sql("ways_nodes", conn, if_exists='replace', index=False)


if __name__ == '__main__':
	main()
	insert_data()