# NAME: Jesse Joseph
# EMAIL: jjoseph@hmc.edu
# ID: 040161840

default: lab3b.py

clean:
	-rm lab3b-040161840.tar.gz

dist: lab3b.py lab3b
	tar -czvf lab3b-040161840.tar.gz README lab3b.py lab3b Makefile
