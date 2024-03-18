#!/usr/bin/env python3
#
# Furnace to Z80 Converter
# Copyright 2024 Nikku4211
#
# Copying and distribution of this file, with or without
# modification, are permitted in any medium without royalty
# provided the copyright notice and this notice are preserved.
# This file is offered as-is, without any warranty.
#
import sys
import struct
from itertools import islice
import numpy as np

def main(argv):
    furcommand = open(argv[1],"rb")
    furdata = furcommand.read()
    
    chan0pointerfur = struct.unpack('<L', furdata[8:12])[0]
    chan1pointerfur = struct.unpack('<L', furdata[12:16])[0]
    chan2pointerfur = struct.unpack('<L', furdata[16:20])[0]
    chan3pointerfur = struct.unpack('<L', furdata[20:24])[0]
    
    chan0pointerz80 = 0
    chan1pointerz80 = 0
    chan2pointerz80 = 0
    chan3pointerz80 = 0
    
    chanxpointerz80 = [chan0pointerz80,chan1pointerz80,chan2pointerz80,chan3pointerz80]
    
    presetdelay = furdata[24:40]
    
    print(presetdelay)
    
    chan0data = furdata[chan0pointerfur:chan1pointerfur]
    chan1data = furdata[chan1pointerfur:chan2pointerfur]
    chan2data = furdata[chan2pointerfur:chan3pointerfur]
    chan3data = furdata[chan3pointerfur:]
    
    chanxdata = [chan0data,chan1data,chan2data,chan3data]
    
    z80tick = open(argv[2], 'wt')
    
    z80byte = 0
    
    z80tick.write("""
.section '%s' free
;this file was converted by Nikku4211's Furnace2Z80.py
%s:\n
  .db $01\n"""
                    % (argv[3], argv[3]))
    
    print(chan0pointerfur)
    z80tick.write('  .dw '
                        + ''.join('$%04x' % chan0pointerfur)
                        + '\n')
    print(chan1pointerfur)
    z80tick.write('  .dw '
                        + ''.join('$%04x' % chan1pointerfur)
                        + '\n')
    print(chan2pointerfur)
    z80tick.write('  .dw '
                        + ''.join('$%04x' % chan2pointerfur)
                        + '\n')
    print(chan3pointerfur)
    z80tick.write('  .dw '
                        + ''.join('$%04x' % chan3pointerfur)
                        + '\n')
                        
    z80byte += 9
    for j in range(4):
        print('channel %1d' % j)
        z80tick.write("""
@ch%1d:\n"""
                    % j)
        chanxpointerz80[j] = z80byte
        for i in range(len(chanxdata[j])):
            if (chanxdata[j][i] > 0xb7 and chanxdata[j][i] < 0xc3) or chanxdata[j][i] == 0xc6 or chanxdata[j][i] == 0xc8 or chanxdata[j][i] == 0xc9:
                continue
                
            if (chanxdata[j][i] > 0xc2 and chanxdata[j][i] < 0xc6) or chanxdata[j][i] == 0xca:
                continue
                
            if chanxdata[j][i] == 0xb7:
                continue
            
            # Python doesn't let me change the i in a for loop, so I got to do this stupid stuff
            if i >= 1:
                if (chanxdata[j][i-1] > 0xb7 and chanxdata[j][i-1] < 0xc3) or chanxdata[j][i-1] == 0xc6 or chanxdata[j][i-1] == 0xc8 or chanxdata[j][i-1] == 0xc9:
                    continue
                    
                if (chanxdata[j][i-1] > 0xc2 and chanxdata[j][i-1] < 0xc6) or chanxdata[j][i-1] == 0xc7 or chanxdata[j][i-1] == 0xca or chanxdata[j][i-1] == 0xfd or chanxdata[j][i-1] == 0xfc:
                    continue
                if i >= 2:    
                    if (chanxdata[j][i-2] > 0xb7 and chanxdata[j][i-2] < 0xc3) or chanxdata[j][i-2] == 0xc6 or chanxdata[j][i-2] == 0xc8 or chanxdata[j][i-2] == 0xc9 or chanxdata[j][i-2] == 0xfc:
                        continue
            
            if chanxdata[j][i] == 0xc7:
                print("volume %2d" % chanxdata[j][i+1])
                z80tick.write('  .db $fb,'
                            + "".join('$%02x' % chanxdata[j][i+1])
                            + '\n')
                z80byte += 2
            
            if chanxdata[j][i] <= 0xb3:
                print(np.clip(chanxdata[j][i]-69, a_min=0, a_max=255))
                z80tick.write('  .db '
                            + ''.join('$%02x' % np.clip(chanxdata[j][i]-69, a_min=0, a_max=255))
                            + '\n')
                z80byte += 1
                            
            if chanxdata[j][i] >= 0xb4 and chanxdata[j][i] <= 0xb5:
                print("note off")
                z80tick.write('  .db $fd, \n')
                z80byte += 1
                
            if chanxdata[j][i] >= 0xe0 and chanxdata[j][i] <= 0xef:
                print("skip %3d frames" % presetdelay[chanxdata[j][i]-0xe0])
                z80tick.write('  .db $fe,'
                            + "".join('$%02x' % presetdelay[chanxdata[j][i]-0xe0])
                            + '\n')
                z80byte += 2
            
            if chanxdata[j][i] == 0xfc:
                print("skip %3d frames" % struct.unpack('<H', chanxdata[j][i:i+2]))
                z80tick.write('  .db $fc,'
                            + "".join('$%02x' % chanxdata[j][i+1])
                            + ","
                            + "".join('$%02x' % chanxdata[j][i+2])
                            + '\n')
                z80byte += 3
            
            if chanxdata[j][i] == 0xfd:
                print("skip %3d frames" % chanxdata[j][i+1])
                z80tick.write('  .db $fe,'
                            + "".join('$%02x' % chanxdata[j][i+1])
                            + '\n')
                z80byte += 2
            
            if chanxdata[j][i] == 0xfe:
                print("skip one frame")
                z80tick.write('  .db $fe,$01 \n')
                z80byte += 2
                            
            if chanxdata[j][i] == 0xff:
                print("end")
                z80tick.write('  .db $ff \n')
                z80byte += 1
    
    z80tick.write(""".ends""")
    
    furcommand.close()
    z80tick.close()
    
    z80tick = open(argv[2], 'rt')
    z80tickbuff = z80tick.readlines()
    
    z80tickbuff[6] = "  .dw " + str(chanxpointerz80[0]) + ' + ' + argv[3] + '\n'
    z80tickbuff[7] = "  .dw " + str(chanxpointerz80[1]) + ' + ' + argv[3] + '\n'
    z80tickbuff[8] = "  .dw " + str(chanxpointerz80[2]) + ' + ' + argv[3] + '\n'
    z80tickbuff[9] = "  .dw " + str(chanxpointerz80[3]) + ' + ' + argv[3] + '\n'
    
    z80tick.close()
    
    with open(argv[2], 'wt') as z80tick:
        z80tick.writelines(z80tickbuff)
    
if __name__=='__main__':
    main(sys.argv)