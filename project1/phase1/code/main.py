import os
import argparse

MemSize = 1000 # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.

'''------------- GLOBALS BELOW ---------------'''

OPCODES = {
    0b0110011: 'R',
    0b0010011: 'I',
    0b1101111: 'J',
    0b1100011: 'B',
    0b0100011: 'S',
    0b0000011: 'LW',
    0b1111111: 'HALT'
}

FUNCT3 = {
    0b000: 'ADS',
    0b100: 'XOR',
    0b110: 'OR',
    0b111: 'AND',
    0b001: 'BNE',
    0b010: 'SW'  
}

FUNCT7 = {
    0b0000000: 'ADD',
    0b0100000: 'SUB'
}

BIT_FIELDS = {
    'R': [7,5,5,3,5,7],
    'I': [12,5,3,5,7],
    'S': [7,5,5,3,5,7], 
    'B': [7,5,5,3,5,7],
    'U': [20,5,7],
    'J': [20,5,7]
}

class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        
        with open(ioDir + "/imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress):
        '''------------- CODE BELOW ---------------'''
        index = int(ReadAddress*4)
        instruction = ""
        for idx in range(index, index+4):
            instruction += self.IMem[idx]
        return instruction
          
class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + "/dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]

    def readMem(self, ReadAddress):
        '''------------- CODE BELOW ---------------'''
        index = ReadAddress
        for idx in range(index, index+4):
            data_instr += self.DMem[idx]
        return data_instr
    
        #return self.DMem[(index) : (index+31)]
        
    def writeDataMem(self, Address, WriteData):
        '''------------- CODE BELOW ---------------'''
        start = 0
        index = Address
        for x in range(0,4):
            self.DMem[index] = WriteData[start : start + 8]
            start += 8
            index+=1
        return 
                   
    def outputDataMem(self):
        resPath = self.ioDir + "/" + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "/RFResult.txt"
        self.Registers = [0x0 for i in range(32)]
    
    def readRF(self, Reg_addr):
        '''------------- CODE BELOW ---------------'''
        return self.Registers[Reg_addr]
    
    def writeRF(self, Reg_addr, Wrt_reg_data):
        '''------------- CODE BELOW ---------------'''
        self.Registers[Reg_addr] = Wrt_reg_data
        return
         
    def outputRF(self, cycle):
        op = ["-"*70+"\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        op.extend([str(val)+"\n" for val in self.Registers])
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)

class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": False, "Instr": 0}
        self.EX = {"nop": False, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "is_I_type": False, "rd_mem": 0, 
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": False, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0, 
                   "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": False, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}

class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem

class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + "/SS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_SS.txt"

    def step(self):
        '''------------------------------ CODE BELOW ---------------------------------'''
        current_instr = self.ext_imem.readInstr(self.state.IF['PC'] / 4)
        current_opcode = OPCODES.get(current_instr[-7:]) # gets current opcode instruction

        seperated_instr = [] # instructions separated by bit fields
        start = 0
        for size in BIT_FIELDS.get(current_opcode):
            seperated_instr.append(current_instr[start: start + size])
            start += size

        #bin(int('1010', 2)) <-- conversion
        #result (rd) = bin(int(a, 2) + int(b, 2))  -> results in a string
        # where a = rs1 (string) and b = rs2 (string) 
        # no need to include another library! (at least for R type)
        match current_opcode: 
            case 'R':
                #seperated_instr[4] = rd, seperated_inst[2] = rs1, seperated_inst[1] = rs2 
                match FUNCT3.get(seperated_instr[3]):
                    case 'ADS':
                        if (FUNCT7.get(seperated_instr[0]) == 'ADD'):
                            rd = bin(int(seperated_instr[2], 2) + int(seperated_instr[1], 2))
                            self.myRF.writeRF(seperated_instr[4], rd)
                            self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                        if (FUNCT7.get(seperated_instr[0]) == 'SUB'):
                            rd = bin(int(seperated_instr[2], 2) - int(seperated_instr[1], 2))
                            self.myRF.writeRF(seperated_instr[4], rd)
                            self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                    case 'XOR':
                        rd = bin(int(seperated_instr[2], 2) ^ int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[4], rd)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                    case 'OR':
                        rd = bin(int(seperated_instr[2], 2) | int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[4], rd)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                    case 'AND':
                        rd = bin(int(seperated_instr[2], 2) & int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[4], rd)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

            case 'I':
                #seperated_instr[3] = rd, seperated_inst[1] = rs1, seperated_inst[0] = imm[11:5]
                #Steps to Solve: First, read the 
                match FUNCT3.get(seperated_instr[2]):
                    case 'ADS': #ADDI
                        spliced = bin(int(seperated_instr[0], 10))
                        data = bin(spliced + int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[3], data)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                    case 'XOR': #XORI
                        spliced = bin(int(seperated_instr[0], 10))
                        data = bin(spliced ^ int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[3], data)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                    case 'OR': #ORI
                        spliced = bin(int(seperated_instr[0], 10))
                        data = bin(spliced | int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[3], data)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

                    case 'AND': #ANDI
                        spliced = bin(int(seperated_instr[0], 10))
                        data = bin(spliced & int(seperated_instr[1], 2))
                        self.myRF.writeRF(seperated_instr[3], data)
                        self.nextState.IF['PC'] = self.state.IF['PC'] + 4

            case 'J':
                imm_20 = bin(int(seperated_instr[0][0], 2)) & 0x1
                imm_19_12 = bin(int(seperated_instr[0][1:8], 2)) & 0xFF
                imm_11 = bin(int(seperated_instr[0][9], 2)) & 0x1
                imm_10_1 = bin(int(seperated_instr[0][10:19], 2)) & 0x3FF
                imm = (imm_20 | imm_19_12 | imm_11 | imm_10_1)

                if imm_20 == 1:
                    imm = imm | 0xFFF00000

                next_cycle = self.state.IF['PC'] + 4
                self.myRF.writeRF(int(seperated_instr[2]), next_cycle) # rd = PC + 4

                pc = self.state.IF['PC'] + (int(imm, 10) * 4)
                self.nextState.IF['PC'] = pc

            case 'B':
                match FUNCT3.get(seperated_instr[3]):
                    case 'ADS': #BEQ
                        imm = seperated_instr[0][0] + seperated_instr[5][4] + seperated_instr[0][1:] + seperated_instr[5][1:3]
                        imm = bin(int(imm), 2)
                        if (bin(int(seperated_instr[1], 2)) == bin(int(seperated_instr[2], 2))):
                            pc = self.state.IF['PC'] + (int(imm, 10) * 4)
                            self.nextState.IF['PC'] = pc
                        else:
                            self.nextState.IF['PC'] = self.state.IF['PC'] + 4
                        
                        pass
                    case 'BNE': 
                        imm = seperated_instr[0][0] + seperated_instr[5][4] + seperated_instr[0][1:] + seperated_instr[5][1:3]
                        imm = bin(int(imm), 2)
                        if (bin(int(seperated_instr[1], 2)) != bin(int(seperated_instr[2], 2))):
                            pc = self.state.IF['PC'] + (int(imm, 10) * 4)
                            self.nextState.IF['PC'] = pc
                        else:
                            self.nextState.IF['PC'] = self.state.IF['PC'] + 4
                        pass
            case 'S': 
                imm = seperated_instr[0] + seperated_instr[4]
                imm = bin(int(imm), 2)
                mem_loc = int(seperated_instr[2]) + (int(imm))
                self.ext_dmem.writeDataMem(mem_loc, self.ext_dmem.readMem(int(seperated_instr[1])))
                self.nextState.IF['PC'] = self.state.IF['PC'] + 4
                pass
            case 'LW':
                imm = seperated_instr[0] + seperated_instr[4]
                imm = bin(int(imm), 2)
                self.myRF.writeRF(int(seperated_instr(3)), self.ext_dmem.readMem(int(seperated_instr[1])))
                self.nextState.IF['PC'] = self.state.IF['PC'] + 4           
                pass
            case 'HALT':
               self.nextState.IF['nop'] = True


        if self.state.IF["nop"]:
            self.halted = True
            
        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
            
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        '''--------------- FIX THIS --------------'''
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")
        
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + "/FS_", imem, dmem)
        self.opFilePath = ioDir + "/StateResult_FS.txt"

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------
        
        
        
        # --------------------- MEM stage --------------------
        
        
        
        # --------------------- EX stage ---------------------
        
        
        
        # --------------------- ID stage ---------------------
        
        
        
        # --------------------- IF stage ---------------------
        
        self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True
        
        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
        
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

if __name__ == "__main__":
     
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    dmem_fs = DataMem("FS", ioDir)
    
    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while(True):
        if not ssCore.halted:
            ssCore.step()
        
        if not fsCore.halted:
            fsCore.step()

        if ssCore.halted and fsCore.halted:
            break
    
    # dump SS and FS data mem.
    dmem_ss.outputDataMem()
    dmem_fs.outputDataMem()
