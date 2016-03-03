import yaml, os, sys

__PATH__       	= os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

def create_new_yml(board):
	fp = file(__PATH__ + "/core/template/template_board.yml")
	lines = []
	for line in fp: 
	    lines.append(line)
	fp.close()

	s = ''.join(lines)

	fp = file(__PATH__ +"/"+ board+".yml", 'w')
	fp.write(s)
	fp.close()
	print ("Create Sucessfully!")

board = raw_input("Board: ")
create_new_yml(board)
os.system("pause")
