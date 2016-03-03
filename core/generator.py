#CPLD AUTO_GENERATOR tool
#Author: Haley(B51762)
#Date: 2015.5.31

import yaml, os, re

##################################################################
#PATH DEFINITION SECTION
##################################################################
#Get current work path
__PATH__       	= os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
__PATH_DIR__ 	= os.path.dirname(__PATH__)

#Output File path definition
VERILOG_OUTPUT_PATH		= __PATH_DIR__ + "/output/my_uart_top.v"
TCL_OUTPUT_PATH			= __PATH_DIR__ + "/output/my_uart_top.tcl"
QSF_OUTPUT_PATH			= __PATH_DIR__ + "/output/my_uart_top.qsf"
#Templat FIle path definiton
TWR_CPLD_IO_PATH		= __PATH__ + "/cpld_io/twr_cpld_io.yml"
TWRV2_CPLD_IO_PATH		= __PATH__ + "/cpld_io/twrv2_cpld_io.yml"
FRDM_CPLD_IO_PATH		= __PATH__ + "/cpld_io/frdm_cpld_io.yml"
EP570_CPLD_IO_PATH      = __PATH__ + "/cpld_io/ep570_cpld_io.yml"
FRDMV2_CPLD_IO_PATH     = __PATH__ + "/cpld_io/frdmv2_cpld_io.yml"

TWR_TEMPLATE_VERILOG_PATH	= __PATH__ + "/template/twr/template_my_uart_top.v"
TWR_TEMPLATE_QSF_PATH   	= __PATH__ + "/template/twr/template_my_uart_top.qsf"
TWR_TEMPLATE_TCL_PATH		= __PATH__ + "/template/twr/template_my_uart_top.tcl"

TWRV2_TEMPLATE_VERILOG_PATH	= __PATH__ + "/template/twrv2/template_my_uart_top.v"
TWRV2_TEMPLATE_QSF_PATH   	= __PATH__ + "/template/twrv2/template_my_uart_top.qsf"
TWRV2_TEMPLATE_TCL_PATH		= __PATH__ + "/template/twrv2/template_my_uart_top.tcl"

FRDM_TEMPLATE_VERILOG_PATH	= __PATH__ + "/template/frdm/template_my_uart_top.v"
FRDM_TEMPLATE_QSF_PATH   	= __PATH__ + "/template/frdm/template_my_uart_top.qsf"
FRDM_TEMPLATE_TCL_PATH		= __PATH__ + "/template/frdm/template_my_uart_top.tcl"

FRDMV2_TEMPLATE_VERILOG_PATH	= __PATH__ + "/template/frdmv2/template_my_uart_top.v"
FRDMV2_TEMPLATE_QSF_PATH   	= __PATH__ + "/template/frdmv2/template_my_uart_top.qsf"
FRDMV2_TEMPLATE_TCL_PATH		= __PATH__ + "/template/frdmv2/template_my_uart_top.tcl"

EP570_TEMPLATE_VERILOG_PATH	= __PATH__ + "/template/ep570/template_my_uart_top.v"
EP570_TEMPLATE_QSF_PATH   	= __PATH__ + "/template/ep570/template_my_uart_top.qsf"
EP570_TEMPLATE_TCL_PATH		= __PATH__ + "/template/ep570/template_my_uart_top.tcl"

#by deafult we think it is twr board
TEMPLATE_VERILOG_PATH       = TWR_TEMPLATE_VERILOG_PATH
TEMPLATE_QSF_PATH           = TWR_TEMPLATE_QSF_PATH
TEMPLATE_TCL_PATH           = TWR_TEMPLATE_TCL_PATH

#CPLD Uart Command:
UART_COMMAND_NUM = 3

#Bus Name Definition
BUS_NAME = ["BusA", "BusB", "BusC", "BusD", "BusE", "BusF", "BusG", "BusH", "BusI", "BusJ"]

#Special CPLD IO,       IO/GCLK: 14,62,64,     IO/DEV: 43,     RESET: 44
#Assign specila_IO as general_IO: add them into Used_io list.
SPECIAL_IO = []


##################################################################
#CODE SYNTAX DEFINITON SECTION
##################################################################
#Quartus TCL Assignment Syntax
Quartus_TCL_ASSIGNMENT_TEXT = "set_location_assignment PIN_%d -to %s[%d]\n"

#Verilog: name reg example(linkSPI)
LINK_NAME = "link%s"

#Verilog: reg **;
REG_TEXT = "reg %s;\n"

#Verilog inout Syntax
INOUT_TEXT = "inout [%d:%d] %s;\n"

#Verilog: assign Bus[1] =  %s? Bus[0] : 1'bz;
ASSIGN_TEXT = "assign %s[%d] =  %s ? %s[%d] : 1'bz;"

#Verilog module definiton Syntax
MODULE_TEXT = "module my_uart_top(clk,rst_n,rs232_rx,rs232_tx, %s led);\n"

#Verilog: reg assignment Syntax
TO_REG_TEXT = "%s <= 1'b%d;\n"

#Verilog: led
LED_TEXT = "\t\t\t  led <= 1'b1;\n"

#Verilog: code block
BLOCK_TEXT ='''
always @ (posedge clk or negedge rst_n)
begin
	if(!rst_n)
	begin
		//////////////////add link here////////////////
%s
		///////////////////////////////////////////////
		led <= 1'b0; // for debug led
	end
	else
	begin
		case(Rx_cmd)
        ///////////////////add case here/////////////
%s
		////////////////////////////////////////////////

			{R,S,T}: //RESET
			   begin
%s
      			led <= 1'b0;
			  end

         default:
			   begin
%s
    			led <= 1'b0;
			end
		endcase
	end
end
'''




##################################################################
#CODE GENERATE SECTION
##################################################################
#Verilog Basic Code syntax
def verilog_name_reg(ModuleName):
	LINKCMD = LINK_NAME%ModuleName
	CodeText = REG_TEXT%LINKCMD
	return CodeText

def verilog_assign(ModuleName, BusNameIN, CPinIN, BusNameOUT, CPinOUT):
	LINKCMD = LINK_NAME%ModuleName
	CodeText = ASSIGN_TEXT%(BusNameOUT,CPinOUT,LINKCMD,BusNameIN,CPinIN)
	return CodeText

def verilog_inout(max,min,busname):
	CodeText = INOUT_TEXT%(max,min,busname)
	return CodeText

#Generate Verilog block code
def Code_verilog_bus_define(bus_scope):
	BusText = ""

	num_bus = len(bus_scope)

	#Generate bus definition code
	for n in xrange(num_bus):
		bus = bus_scope[n]
		BusText += verilog_inout(bus[1], bus[0], BUS_NAME[n])

	#Generate ModuleText
	ModuleTitle = ""
	for i in BUS_NAME[:num_bus]:
		ModuleTitle += i+","
	ModuleTitle = MODULE_TEXT%ModuleTitle

	return ModuleTitle, BusText

def Code_verilog_assign_part(io_dic, BusScope):
	AssignText = ""
	RegText    = ""

	#generate reg and assign code
	for cmd in io_dic:
		conns = io_dic[cmd]
		module_name = conns[-1]

		#generate reg code
		RegText += verilog_name_reg(cmd)
		#generate Moudle comments
		AssignText += "//%s  ---  %3s\n"%(module_name, cmd)

		io_infos = conns[0:-1]

		for io in io_infos:
			#judge io in which bus
			for n  in xrange(len(BusScope)):
				if BusScope[n][0] <= io[0] <= BusScope[n][1]:
					busin =  BUS_NAME[n]
			for n  in xrange(len(BusScope)):
				if BusScope[n][0] <= io[1] <= BusScope[n][1]:
					busout = BUS_NAME[n]
			#generate assign code
			AssignText += verilog_assign(cmd, busin, io[0], busout, io[1]) + "  " + io[2] + "\n"
		AssignText += "\n"

	print AssignText

	#merge AssignText into RegText
	RegText += "\n\n" + AssignText

	return RegText

def Code_verilog_reg(io_dic):
	to_reg_dic = {}
	for cmd in io_dic:
		LINKCMD = LINK_NAME%cmd
		to_reg_dic[cmd] = (TO_REG_TEXT%(LINKCMD, 0),TO_REG_TEXT%(LINKCMD, 1))

	CMD_Text = ""
	RST = ""
	for cmd in to_reg_dic:
		v = to_reg_dic[cmd]
		CMD_Text += "			{%s,%s,%s}:\n\t\t\tbegin\n"%(cmd[0], cmd[1],cmd[2]) + "\t\t\t  " + v[1]
		CMD_Text += LED_TEXT + "\t\t\tend\n\n"
		RST += "			 " + v[0]

	TEXT = BLOCK_TEXT%(RST,CMD_Text,RST,RST)
	return TEXT

#generate tcl code
def Code_tcl_assignments(used_io, bus_scope, tab=False):
	Text = ""
	for io in used_io:
		for n  in xrange(len(bus_scope)):
			bus = bus_scope[n]
			if bus[0] <= io <= bus[1]:
				sentence = Quartus_TCL_ASSIGNMENT_TEXT%(io, BUS_NAME[n], io)
				if tab is True:
					Text += "\t"+ sentence
				else:
					Text += sentence
				break
	return Text








##################################################################
#FILE OPERATIONS SECTION
##################################################################
def file_load_yml(fp):
	try:
		f = open(fp,"r")
	except IOError:
		print ("Error: No such file %s"%fp)
		return None

	c = {}
	try:
		c = yaml.load(f)
	except yaml.parser.ParserError:
		print ("Error: There may be some format errors exist in Yaml File.\n%s"%fp)
		return None

	f.close()
	return c

#write to new file
def file_write_to_new(template_file, output_file, modify_part):
	fp = file(template_file)
	lines = []
	for line in fp:
		lines.append(line)
	fp.close()

	positions = modify_part.keys()	#get key list, and name it positions
	positions.sort()				#sort position list
	positions = positions[::-1]		#reverse positions list

	for position in positions:
		text = modify_part[position]
		lines.insert(position-1, text)

	s = ''.join(lines)
	fp = file(output_file, 'w')
	fp.write(s)
	fp.close()






##################################################################
#CPLD PINS PARSER SECTION
##################################################################
def look_up_table(content,pin,type):
#look up pins in cpld_io.yml
	for i in content:
		if   (content[i]["PINS"] == pin and (content[i]["TYPE"] == type or content[i]["TYPE"] == 'NONE'))or(content[i]["FUNC"] == pin):
			return i, content[i]["PINS"]

	if pin is None:
		print ("Error: Empty Tag: \'%s\'"%type)
	else:
		if type == "T": type = "Target"
		else          : type = "Assistant"
		print ("Error: Specific \'%s : %s\' not connected with the CPLD!\n")%(type,pin)

	return None,None

#For FRDM-Series
def remap_pin(pin):
	character = pin[0]
	digit     = int(pin[1:])
	digit     = str(2 + 2*(digit-1))
	pin       = character + digit
	return pin

#look up io in cpld_io dic
#return:  [(CpldIOIn0,CpldIoOut0,Comments),....]    type[list]
#switch: single row need to remap, this value set True
def look_up(cpld_io, module, switch):

	mname = module["CMD"]

	confuncs = module.keys()
	confuncs.remove("CMD")
	confuncs.sort()

	look_result = []

	for conname in confuncs:
		connection = module[conname]

		if "T_PIN" in connection and "A_PIN" in connection and "DIRECTION" in connection:
			CON_TYPE = "TA"
			tp = connection["T_PIN"]
			ap = connection["A_PIN"]
			if switch is True and not re.search("CPLD_IO", tp):
				tp = remap_pin(tp)
		elif "T_PIN_1" in connection and "T_PIN_2" in connection and "DIRECTION" in connection:
			CON_TYPE = "TT"
			tp = connection["T_PIN_1"]
			ap = connection["T_PIN_2"]
			if switch is True:
				if not re.search("CPLD_IO", tp):
					tp = remap_pin(tp)
				if not re.search("CPLD_IO", ap):
					ap = remap_pin(ap)
		else:
			print ("Parse Error: Invalid Lable in %s"%connection)
			return None

		#look up the table of cpld-io
		#CPinIN:  CPLD in
		#CPinOUT: CPLD out
		#comments: code comments
		if  CON_TYPE == "TA" and connection["DIRECTION"] == "T2A":
			CPinIN , tp = look_up_table(cpld_io,tp,"T")
			CPinOUT, ap = look_up_table(cpld_io,ap,"A")
			arrow   = " -> "
			comments = "//%4s  %8s(T)%s%4s(A)"%(conname,tp,arrow,ap)

		elif CON_TYPE == "TA" and connection["DIRECTION"] == "A2T":
			CPinIN , ap = look_up_table(cpld_io,ap,"A")
			CPinOUT, tp = look_up_table(cpld_io,tp,"T")
			arrow   = " <- "
			comments = "//%4s  %8s(T)%s%4s(A)"%(conname,tp,arrow,ap)

		elif CON_TYPE == "TT" and connection["DIRECTION"] == "T2T":
			CPinIN , tp = look_up_table(cpld_io,tp,"T")
			CPinOUT, ap = look_up_table(cpld_io,ap,"T")
			arrow   = " -> "
			comments = "//%4s  %8s(T)%s%4s(T)"%(conname,tp,arrow,ap)
		else:
			print ("Parse Error: Not Defined DIRECTION! %s"%connection)
			return None



		if CPinIN is not None and CPinOUT is not None:
			look_result.append((CPinIN,CPinOUT,comments))
		else:
			return None

	return look_result


def map(modules, cpld_io):
	'''
	Struct io_dic:

	module0: [(ioin0,inout0,comments),...(ioin,ioout,comments)]
		...
	'''
	SingF  = 0
	switch = False

	try:
		SingF = modules["SINGLE"]
		del modules["SINGLE"]
	except KeyError:
		pass

	if SingF == 1:
		switch = True


	io_dic = {}

	#look up io in cpld for each module
	for key in modules:
		module = modules[key]
		CMD = module["CMD"]
		io_dic[CMD] = look_up(cpld_io, module,switch)
		if io_dic[CMD] is None:
			print ("Error: Pin error, Please check your yml file at module: \'%s\'."%key)
			return None
		io_dic[CMD].append(key)
	return io_dic


#cpld ip analyze: divide bus
def cpld_io_analyze(io_dic):
	#initial Used_io list
	Used_io = SPECIAL_IO

	for key in io_dic:
		tem = io_dic[key][0:-1]
		for i in tem:
			if i[0] not in Used_io:
				Used_io.append(i[0])
			if i[1] not in Used_io:
				Used_io.append(i[1])
	#sort list
	Used_io.sort()

	print "Used IO-Pins: ",Used_io

	MAX   = 0
	MIN   = Used_io[0]
	scope = []

	#Divide Bus Scope
	for i in xrange(1,len(Used_io)):
		if Used_io[i] - Used_io[i-1] > 10:
			MAX = Used_io[i-1]
			scope.append((MIN,MAX))
			MIN = Used_io[i]
	MAX = Used_io[-1]
	scope.append((MIN,MAX))

	num_bus = len(scope)

	#Bus Definition
	if num_bus > len(BUS_NAME):
		print "Error: The number of bus-name is less than scope."
		return None, None, None

	SUM = 0
	for n in xrange(num_bus):
		bus = scope[n]
		SUM += bus[1] - bus[0] + 1
		if SUM > 76:
			print "Auto-Bus Definition Error:",scope
			return None,None,None

	return Used_io, scope







##################################################################
#WRITE TO NEW FILE SECTION
##################################################################
def generate_tcl_scripts(used_io, bus_scope):
	global TEMPLATE_TCL_PATH
	Text = Code_tcl_assignments(used_io, bus_scope,tab=True)
	modify_part = {81:Text}
	file_write_to_new( TEMPLATE_TCL_PATH, TCL_OUTPUT_PATH, modify_part )

def generate_qsf_file(used_io, bus_scope):
	global TEMPLATE_QSF_PATH
	Text = Code_tcl_assignments(used_io, bus_scope,tab=False)
	modify_part = {64:Text}
	file_write_to_new( TEMPLATE_QSF_PATH, QSF_OUTPUT_PATH, modify_part )

def generate_top_v_file(used_io, bus_scope, io_dic):
	global TEMPLATE_VERILOG_PATH
	#1> module title and bus definiton
	ModuleTitle, BusText = Code_verilog_bus_define(bus_scope)

	print "\n",BusText

	#2> reg definition and assign
	AssignTEXT = Code_verilog_assign_part(io_dic,bus_scope)
	if AssignTEXT is None:
		print ("Error: assign part")
		return None

	#3> Last text generate
	LastText = Code_verilog_reg(io_dic)

	modify_part = {3: ModuleTitle, 11: BusText , 98: AssignTEXT, 232:LastText}
	#add new code into template, and create new file
	file_write_to_new(TEMPLATE_VERILOG_PATH, VERILOG_OUTPUT_PATH, modify_part)





##################################################################
#AUTO-GENERATE-API
##################################################################
def generate(boardyml):
	global TEMPLATE_VERILOG_PATH
	global TEMPLATE_QSF_PATH
	global TEMPLATE_TCL_PATH
	global TWR_TEMPLATE_VERILOG_PATH
	global TWR_TEMPLATE_QSF_PATH
	global TWR_TEMPLATE_TCL_PATH
	global FRDM_TEMPLATE_VERILOG_PATH
	global FRDM_TEMPLATE_QSF_PATH
	global FRDM_TEMPLATE_TCL_PATH
	#Judge "TWR" or "FRDM"
	if  re.search("twr",os.path.basename(boardyml)):
		if re.search("v2", os.path.dirname(boardyml)):
			cpld_io_path = TWRV2_CPLD_IO_PATH
			TEMPLATE_VERILOG_PATH       = TWRV2_TEMPLATE_VERILOG_PATH
			TEMPLATE_QSF_PATH           = TWRV2_TEMPLATE_QSF_PATH
			TEMPLATE_TCL_PATH           = TWRV2_TEMPLATE_TCL_PATH
		else:
			cpld_io_path = TWR_CPLD_IO_PATH
			TEMPLATE_VERILOG_PATH       = TWR_TEMPLATE_VERILOG_PATH
			TEMPLATE_QSF_PATH           = TWR_TEMPLATE_QSF_PATH
			TEMPLATE_TCL_PATH           = TWR_TEMPLATE_TCL_PATH
	elif re.search("frdm",os.path.basename(boardyml)):
		if re.search("v2", os.path.dirname(boardyml)):
			cpld_io_path = FRDMV2_CPLD_IO_PATH
			TEMPLATE_VERILOG_PATH       = FRDMV2_TEMPLATE_VERILOG_PATH
			TEMPLATE_QSF_PATH           = FRDMV2_TEMPLATE_QSF_PATH
			TEMPLATE_TCL_PATH           = FRDMV2_TEMPLATE_TCL_PATH
		else:
			cpld_io_path = FRDM_CPLD_IO_PATH
			TEMPLATE_VERILOG_PATH       = FRDM_TEMPLATE_VERILOG_PATH
			TEMPLATE_QSF_PATH           = FRDM_TEMPLATE_QSF_PATH
			TEMPLATE_TCL_PATH           = FRDM_TEMPLATE_TCL_PATH
	elif re.search("ep570", os.path.basename(boardyml)):
		cpld_io_path = EP570_CPLD_IO_PATH
		TEMPLATE_VERILOG_PATH       = EP570_TEMPLATE_VERILOG_PATH
		TEMPLATE_QSF_PATH           = EP570_TEMPLATE_QSF_PATH
		TEMPLATE_TCL_PATH           = EP570_TEMPLATE_TCL_PATH
	else:
		print "Error: Unknown Yaml File!"
		return

	#ensure ../output exists
	if not os.path.exists(__PATH_DIR__+ "/output"):
	 	os.makedirs(__PATH_DIR__+ "/output")

	#load yml files
	modules = file_load_yml( boardyml )
	cpld_io = file_load_yml( cpld_io_path )
	if modules is None or cpld_io is None:
		print ("Error: Load file error.")
		return None


	#map cpld pins with boards(target & assitant), return a dic
	io_dic = map(modules, cpld_io)
	if io_dic is None:
		return None

	used_io, bus_scope = cpld_io_analyze(io_dic)
	if used_io is None:
		print ("Error: Bus Definition!")
		return None


	#Generate  my_uart_top.tcl
	#---------------------------------------------
	#---------------------------------------------
	generate_tcl_scripts(used_io, bus_scope)

	#Generate  my_uart_top.qsf
	#---------------------------------------------
	#---------------------------------------------
	generate_qsf_file(used_io, bus_scope)

	#Generate  my_uart_top.v
	#---------------------------------------------
	#---------------------------------------------
	generate_top_v_file(used_io, bus_scope, io_dic)

	print ("Generate Successfully!")