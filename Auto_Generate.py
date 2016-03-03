import sys, os
import core.generator

__PATH__ = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')

if __name__ == '__main__':
	print (" Verilog Code Generator Tool")
	print (" -----------------------------------\n")
	
	g = core.generator
	
	if len(sys.argv)== 1:
		boardyml = raw_input("Please input yaml file path\n>>")
	else:
		boardyml = sys.argv[1]

	if os.path.exists(boardyml) is True:
		g.generate(boardyml)
	else:
		print ("error path: %s"%boardyml)

	os.system("pause")