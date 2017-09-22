# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 13:14:41 2015

@author: FELLab
"""

import visa
import numpy as np

WANTED_AVERAGES = 10
MAX_MISSES = 3

def main():
    missed = 0
    rm = visa.ResourceManager()
    try:
        inst = rm.get_instrument("GPIB0::3::INSTR")
    except:
        print(rm.list_resources())
        return # maybe add better error
    
    inst.write("S1") # No averaging
    inst.write("D1") # read CHA
    inst.write("T1") # give me chA
    
    values = list()
    for i in range(WANTED_AVERAGES):
        print("Waiting for pulse {},".format(i), end=' ')
        try:
            # Get the energy
            # return is 
            # "[A:B]:#.### E# \n"
        
            # Don't need to query each time you want a
            # new value. Just read the buffer
            val = inst.read_raw()
            # Trim the \n
            # Split on the : and take the second part
            # remove white space
            # convert to float
            # maybea better way to do it, but meh
            values.append(
                float(val[:-1].split(":")[1].replace(" ",""))
                )
            print("OK: {:.3f} mJ".format( values[-1]*1000))
        except:
            missed += 1 
            print("missed pulse?")
        if missed >= MAX_MISSES:
            print("Missed too many pulses. Is the FEL on?")
            break
    
    st = "Wanted {} Pulses, got {} Pulses: \n\
          \t Average = {:.3f} mJ\n\
          \t std     = {:.3f} mJ"
    print(st.format(WANTED_AVERAGES,
                    len(values),
                    np.mean(values) * 1000,
                    np.std(values) * 1000
    ))
    
    inst.close()
          
if __name__ == "__main__":
    main()