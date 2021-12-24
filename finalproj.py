#author :  neelima chowdary battula
#status : developed

import queue as q
from threading import Thread
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H_%M_%S")

bnk_grp_p = 0
bnk_p = 0
row_p = 0
column_p = 0
debug = 1
Request = ""
CurrentTime = 0
first_instruction_flag = 1
# ------------------------ constants --------------------------------------------------------

tRCD = 24
tCWD = 20
tCAS = 24
tBurst = 4
tWTR = 12
tRAS = 52
tRTP = 12
tRP = 24
tWR = 20
tRRDL = 6
tRRDS = 4
tCCDL = 8
tCCDS = 4
tWTRL = 12
tWTRS = 4

cpu_dram_clk_ratio = 2

input_trace='Trace'
TraceFile = open(input_trace+'.txt')

# ----------------------  act , write , instruction fetch cmds -------------------------------------

READ = '0'
WRITE = '1'
FETCH = '2'

# -------------------------------------------------------------------------------------------
bnk_grp, bnk = (4, 4)
open_page = [[0 for x in range(bnk)] for y in range(bnk_grp)]

# -----------------------------------------flags------------------------------------------------

activate_flag = 0
q_ins = q.Queue()


# ------------------------------------------------------------------------------------------


def MagicHappensHere(Request):
    '''

    :param Request: the dram request
    :return: updated time
    '''
    global first_instruction_flag
    global CurrentTime
    global open_page  # to keep track of all open pages of dram

    output_file = open(input_trace+"result"+str(current_time)+ ".txt", "a")
    print("Current time....", CurrentTime if debug else "")
    print("Request being served......", Request if debug else "")
    #print("Open_page has.............", open_page if debug else "")

    time, current_operation, address = Request.split()

    address = int(address, 16)
    address = bin(address)[2:].zfill(33)

    bnk_grp_n = hex(int(address[25:27], 2))  # Splitting up all the bank, column  and row bits from the address in the request
    bnk_n = hex(int(address[23:25], 2))
    high_col_n = address[15:23]
    low_col_n = address[27:30]
    row_n = hex(int(address[0:15], 2))
    column_n = hex(int(high_col_n, 2))

    if first_instruction_flag:  # services the first request of the queue
        if current_operation == READ or current_operation == FETCH:

            print("activate current time, bank, bank_grp, row", CurrentTime, bnk_n, bnk_grp_n, row_n if debug else "")

            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

            print("read current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n, column_n if debug else "")
            output_file.write(str(CurrentTime).ljust(10) + 'RD'.ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

            first_instruction_flag = 0

        else:

            print("activate current time, bank, bank_grp, row", CurrentTime, bnk_n, bnk_grp_n, row_n if debug else "")
            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n, row_n if debug else "")
            output_file.write(str(CurrentTime).ljust(10)+"WR".ljust(10) + str(bnk_n)[2:].ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n
            first_instruction_flag = 0

    else:
        # comparing the bank groups
        global bnk_grp_p
        global bnk_p
        global row_p
        global prev_operation
        global column_p

        if bnk_grp_p == bnk_grp_n:
            # ------------------>> services the request when the previous requested bank group is same as current requested bank group <<------------------------
            if bnk_p == bnk_n:
                # -------------->> services the request when the previous requested bank is same as current requested bank <<-------------------------------------
                if row_p == row_n:
                    # ---------->> services the request when the previous requested row is same as current requested row <<----------------------------------------

                    if prev_operation == READ or prev_operation == FETCH:
                        if current_operation == READ or current_operation == FETCH:

                            CurrentTime = CurrentTime + (tCCDL) * cpu_dram_clk_ratio

                            # -->> services the request when the previous requested operation is read or fetch and current requested operation is read or fetch <<----

                            print("read current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:
                            # ----------------->> services the request when the current requested operation is write <<-------------------------------------------

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:  # << previous requested operation write>>
                        if current_operation == READ or current_operation == FETCH:  # <<current requested operation read or fetch>>

                            CurrentTime = CurrentTime + tWTRL

                            print("read current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:  # <<handling write request>>

                            CurrentTime = CurrentTime + (tCCDL) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst ) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                else:
                    # ------------------>> services the request when previous requested row is different from the current requested row <<--------------------------------
                    if prev_operation == READ or prev_operation == FETCH:  # << previous request operation is read or fetch >>

                        if current_operation == READ or current_operation == FETCH:  # << current requested operation read or fetch >>

                            CurrentTime = CurrentTime + tRTP*CurrentTime
                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,
                                  row_p if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")
                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time, bank, bank_grp, row", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n


                        else:  # << handling write request >>---------------------------
                            CurrentTime = CurrentTime + tRTP*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")
                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:  # <<previous requested operation write>>

                        if current_operation == READ or current_operation == FETCH:  # <<handling read or fetch request>>

                            CurrentTime = CurrentTime + tWR*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,
                                  row_p if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")

                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD + tWTRL) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(
                                str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:  # <<handling write request>>
                            CurrentTime = CurrentTime + tWR*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,
                                  row_p if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")

                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

            else:
                # -------------------->> services the request when previous requested bank is different from the current bank <<------------------------------------
                if open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] == 0:  # <<check for closed page>>
                    if prev_operation == READ or prev_operation == FETCH:  # << previous request is read or prefetch>>
                        if current_operation == READ or current_operation == FETCH:  # <<handling read or prefetch request>>

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n
                        else:  # <<handling write request>>

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD + tWTRL) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:  # <<previous requested operation write>>
                        if current_operation == READ or current_operation == FETCH:  # <<handling read or fetch request>>

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD + tWTRL) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:  # <<handling write request>>
                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n


                elif open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] == row_n:

                    # .................<<check for open page and activated row is same as requested row>>....................................

                    if prev_operation == READ or prev_operation == FETCH:  # << previous requested operation is read or fetch>>
                        if current_operation == READ or current_operation == FETCH:  # << current requested operation read or fetch>>
                            CurrentTime = CurrentTime + (tCCDL) * cpu_dram_clk_ratio
                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio  # tRCD+

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:  # <<handling write request>>

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:  # << previous requested operation is write >>
                        if current_operation == READ or current_operation == FETCH:  # << handling read request>>

                            CurrentTime = CurrentTime + (tWTR) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio  # tRCD+

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:  # << handling write request>>

                            CurrentTime = CurrentTime + (tCCDL) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio  # tRCD+

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                else:  # <<open page ,activated row is different from requested row >>
                    if prev_operation == READ or prev_operation == FETCH:  # <<previous request is read or fetch>>

                        if current_operation == READ or current_operation == FETCH:  # <current_request is read or fetch>>
                            CurrentTime = CurrentTime + tRTP*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")
                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time, bank, bank_grp, row", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n


                        else:  # <<current request is write>>

                            CurrentTime = CurrentTime + tRTP*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,row_p if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")
                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:  # << previous request is write>>

                        if current_operation == READ or current_operation == FETCH:  # <<cuurrent request is read or fetch>>

                            CurrentTime = CurrentTime + tWR*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,
                                  row_p if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")

                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD + tWTRL) * cpu_dram_clk_ratio

                            print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                        else:  # <<current operation is write>>
                            CurrentTime = CurrentTime + tWR*cpu_dram_clk_ratio

                            print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,row_p if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")

                            CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                            print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                            print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,
                                  column_n if debug else "")
                            output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                            CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                            open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n



        else:
            # -------------------services the request when the previous requested bank group different from current requested bank group-------------------
            if open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] == 0:
                if prev_operation == READ or prev_operation == FETCH:
                    if current_operation == READ or current_operation == FETCH:

                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                              row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                        print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n
                    else:

                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD + tWTRS) * cpu_dram_clk_ratio

                        print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCWD) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                else:
                    if current_operation == READ or current_operation == FETCH:

                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                              row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD + tWTRS) * cpu_dram_clk_ratio

                        print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,
                              column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:] .ljust(10)+ str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:
                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                        print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n



            elif open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] == row_n:
                if prev_operation == READ or prev_operation == FETCH:
                    if current_operation == READ or current_operation == FETCH:

                        CurrentTime = CurrentTime + (tCCDS) * cpu_dram_clk_ratio

                        print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:

                        #CurrentTime = CurrentTime + (r_to_w_delay) * cpu_dram_clk_ratio  # tRCD+

                        print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                else:
                    if current_operation == READ or current_operation == FETCH:

                        CurrentTime = CurrentTime + (tWTR) * cpu_dram_clk_ratio

                        print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio  # tRCD+

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:

                        CurrentTime = CurrentTime + (tCCDS) * cpu_dram_clk_ratio

                        print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio  # tRCD+

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

            else:
                if prev_operation == READ or prev_operation == FETCH:

                    if current_operation == READ or current_operation == FETCH:  # current_operation

                        CurrentTime = CurrentTime + tRTP*cpu_dram_clk_ratio

                        print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")
                        CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                        print("activate current time, bank, bank_grp, row", CurrentTime, bnk_n, bnk_grp_n,
                              row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                        print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n


                    else:

                        CurrentTime = CurrentTime + tRTP*cpu_dram_clk_ratio

                        print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")
                        CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                        print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCWD) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                else:

                    if current_operation == READ or current_operation == FETCH:

                        CurrentTime = CurrentTime + tWR*cpu_dram_clk_ratio

                        print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,row_p if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")

                        CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD + tWTRS) * cpu_dram_clk_ratio

                        print("read current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "RD".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCAS + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

                    else:
                        CurrentTime = CurrentTime + tWR*cpu_dram_clk_ratio

                        print("precharge current time,bank,bank_grp,row ", CurrentTime, bnk_p, bnk_grp_p,row_p if debug else "")

                        output_file.write(str(CurrentTime).ljust(10) + "PRE".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_p)[2:] + "\n")

                        CurrentTime = CurrentTime + tRP*cpu_dram_clk_ratio

                        print("activate current time,bank,bank_grp,row ", CurrentTime, bnk_n, bnk_grp_n,row_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "ACT".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(row_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tRCD) * cpu_dram_clk_ratio

                        print("write current time,bank,bank_grp,row", CurrentTime, bnk_n, bnk_grp_n,column_n if debug else "")
                        output_file.write(str(CurrentTime).ljust(10) + "WR".ljust(10) + str(bnk_grp_n)[2:].ljust(10) + str(bnk_n)[2:].ljust(10) + str(column_n)[2:] + "\n")

                        CurrentTime = CurrentTime + (tCWD + tBurst) * cpu_dram_clk_ratio

                        open_page[int(bnk_grp_n, 16)][int(bnk_n, 16)] = row_n

    bnk_grp_p = bnk_grp_n
    bnk_p = bnk_n
    row_p = row_n
    column_p = column_n
    prev_operation = current_operation
    output_file.close()
    return CurrentTime


def insert_to_queue():
    '''
    reads the requests from the text file and inserts the requests into the queue
    :return: none
    '''
    global Request

    # QueueEmpty=(q_ins.size()==0)
    if debug:
        print("Queue size", q_ins.size() if debug else "")

    while (not q_ins.size() == 16):
        try:
            Request = TraceFile.readline()
            if len(Request.split()) == 3:
                q_ins.enqueue(Request)
                RequestTime = int(Request[0:2])
                if debug:
                   print("Current_request", Request if debug else "")

            elif not (Request):
                break
            else:
                print("invalid Request", Request)
        except Exception as e:
            print("unable to read file...")
            break


def del_frm_queue():
    '''
    pop the handled request and insert the next request into the queue
    :return: none
    '''
    global first_instruction_flag
    #print("thread two started......" if debug else "")
    while (1):
        if (q_ins.size() != 0):
            global CurrentTime
            Request_in_queue = q_ins.get_queue_top()

            #print("CurrentTime---------------------------->>", CurrentTime if debug else "")
            if first_instruction_flag:
                #print("first_instruction_flag.............", first_instruction_flag if debug else "")
                CurrentTime = CurrentTime + int(Request_in_queue.split()[0]) + 2  # for the first instruction since dram clock is double the cpu clock 2 extra cpu cycles were added
                print("************",Request_in_queue.split()[0])
            if CurrentTime>=int(Request_in_queue.split()[0]):
                CurrentTime = MagicHappensHere(Request_in_queue)
            else:
                CurrentTime = int(Request_in_queue.split()[0])+2
                CurrentTime = MagicHappensHere(Request_in_queue)


            dequeued_elements = q_ins.dequeue()  # pop from queue
            request = TraceFile.readline()
            if request != '':
                q_ins.enqueue(request)  # insert next element

            print("\n elements are dequeued", dequeued_elements if debug else "")
            #print("queue size, Current_request", q_ins.size(), request if debug else "")
            # print("queue after", q_ins.read_queue())


thread2 = Thread(target=del_frm_queue)
thread1 = Thread(target=insert_to_queue)

thread2.start()
thread1.start()












