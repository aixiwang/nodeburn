#--------------------------------------------------------
# nodeburn v03 -- a tool to upload lua script to NodeMCU
# BSD license is applied to this code
# Copyright by Aixi Wang (szwax888@126.com)
#
# How to use:
# python nodeburn.py serial_port_name lua_filename
# example:
#     nodeburn.py COM3 file.format  -- format spi filesystem
#     nodeburn.py COM3 init.lua     -- download init.lua
#--------------------------------------------------------
import serial
import sys,time

global lua_line_index
lua_line_index = 0

#----------------------
# lua_sendcmdline
#----------------------
def lua_sendcmdline(cmd):
    print 'cmdline:' + cmd
    global lua_line_index   
    
    cmd2 = cmd + '\r'
    #print '{'+cmd2    
    for i in range(0,len(cmd2)):
        s.write(cmd2[i])
        resp_c = ''
        resp_c = s.read(1)
        #print 'resp_c chr=',str(ord(resp_c))
        if (resp_c == cmd2[i]):
            continue
    resp = ''        
    resp = s.read(3)

    #print '}' + resp
    if (resp[0:3] == '\n> ' or resp[0:3] == '\n>>'):
        print 'L' + str(lua_line_index) +'.'
        pass
        
    else:
        print '[error]'
        c = ''
        line = ''
        while (c != '>'):
            c = s.read(1)
            line += c
        print 'L' + str(lua_line_index) +'.'
        print cmd
        print resp+line            
        lua_sendcmdline2(']]]')
        sys.exit(-1)

#----------------------
# lua_sendcmdline2
#----------------------
def lua_sendcmdline2(cmd):
    cmd2 = cmd + '\r'
    s.write(cmd2)
    while True:
        c = s.read(1)
        if c == '>':
            c2 = s.read(1)
            if c2 == ' ':
                return
    
#-------------------------
# main
#-------------------------
if __name__ == '__main__':
    serialport_path = sys.argv[1]
    serialport_baud = 9600
    s = serial.Serial(serialport_path,serialport_baud)

    lua_sendcmdline2(']]]')    
    lua_sendcmdline2('')
    lua_sendcmdline2('')

    if sys.argv[2] == 'file.format':
        print 'format spi filesystem'
        lua_sendcmdline('file.format()')
        sys.exit(0)

    lua_filename = sys.argv[2]        
    f = open(lua_filename,'r')        
    lua_sendcmdline('file.remove("%s")' % (lua_filename))
    lua_sendcmdline('file.open("%s","w+")' %(lua_filename))

    line = f.readline()

    while line:
        #print 'f->' + line
        line = line.rstrip('\n')
        line = line.rstrip('\r')
        lua_line_index += 1
        
        skip = 0
        skip2 = 0
        if len(line) == 0:
            skip = 1
        elif line.find('--') == 0 and skip2 != 1:
            print 'find --, skip, line:' + str(lua_line_index)
            skip = 1
        elif line.find('--[[') == 0:
            print 'find --[[, skip, line:' + str(lua_line_index)       
            skip = 1
            skip2 = 1
        elif line.find('/*') == 0:    
            skip = 1
            skip2 = 1
        elif line.find(']]') >= 0 and skip2 == 1:
            skip = 1
            skip2 = 0
        elif line.find('*/') >= 0 and skip2 == 1:
            skip = 1
            skip2 = 0
        else:
            if skip2 == 1:
                print 'skip, line:' + str(lua_line_index)       
                skip = 1
            else:
                skip = 0
                    
        if skip == 0:
            lua_sendcmdline('file.writeline([[%s]])' % (line))
            #lua_sendcmdline('tmr.wdclr()')
        line = f.readline()
        
    f.close()

    lua_sendcmdline('file.close()')
    lua_sendcmdline('node.restart()')
    #lua_sendcmdline2('dofile("%s")' % (lua_filename))
    s.close()