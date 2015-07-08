#!/usr/bin/python

import cgi



#main program

if __name__ == "__main__":
	try:
		print("""Contern-type:text/html\n\n <!DOCTYPE html>""")
		print("hello world")
	except:
		cgi.print_exception()

