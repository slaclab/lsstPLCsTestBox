from tester import Test
from pluto_gateway import PlutoGateway
from test_box import TestBox
import random
import time


class TestTemplate(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "Template"
        self.desc = "Template"

    def test(self):
        self.step("Initial message.")
        if False:
            self.step("Failure message.")
            return False
        self.step("Success message")
        return True


class TestPlutoConnect (Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestPlutoConnect"
        self.desc = "Connect to Pluto Gateway: 192.168.1.100:502"

    def test(self):
        try:
            self.step("Trying to connect to Pluto Gateway.")
            self.tester.plutoGateway = PlutoGateway(self.tester)
            for ch in self.tester.plutoGateway.channels:
                self.log(str(ch.read()))

        except Exception as e:
            self.step("Can't connect to Pluto Gateway :: "+str(e))
            return False

        self.step("Successfully connected to Pluto Gateway")
        return True


class TestTestBoxConnect(Test):
    def __init__(self, tester, id):
        Test.__init__(self, tester, id)
        self.name = "TestTestBoxConnect"
        self.desc = "Connect to Test Box: 192.168.1.101:502"

    def test(self):
        try:
            self.step("Trying to connect to Test Box.")
            self.tester.testBox = TestBox(self.tester)

            for ch in self.tester.testBox.plc.channels:
                self.log(str(ch.read()))

            for ch in self.tester.testBox.cam.channels:
                self.log(str(ch.read()))

        except Exception as e:
            self.step("Can't connect to Test Box :: " + str(e))
            return False

        self.step("Successfully connected to Test Box")
        return True


class TestPlutoGatewayConfig(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestPlutoGatewayConfig"
        self.expected_config = [0, 3, 1000, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 0,
                                    0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.desc = "Check Pluto Gateway configuration registers. Expected:" + str(self.expected_config)

    def test(self):
        config = self.tester.plutoGateway.read_holding_registers(4, 0, 42)
        for i in range(len(self.expected_config)):
            if config[i] != self.expected_config[i]:
                self.step(("Pluto Gateway Config doesn't match expected values.\nConfig:\t\t%s\nExpected config:%s" % (
                str(config), str(self.expected_config))))
                return False
        self.step(("Pluto Gateway Config match expected values.\nConfig:\t\t%s \nExpected config:%s"%(str(config),str(self.expected_config))))
        return True


class TestPlutoPLCsPresent(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestPlutoPLCsPresent"
        self.desc = "Check Pluto Gateway sees Pluto D45 as node 0."

    def test(self):
        mask = self.tester.plutoGateway.read_holding_registers(36, 1, 1)[0]

        if mask == 0:
            self.step("Pluto Gateway doens't see any PLC")
            return False
        elif mask != 1:
            self.step(
                "Pluto Gateway see a PLC(s) in  unexpected nodes adds. Binary mask for detected PLCs:{0:b}".format(
                    mask))
            return False

        self.step(("Pluto Gateway sees D45 PLC as node 0"))
        return True


class TestPlutoWriteRegisters(Test):
    def __init__(self, tester, id):
        Test.__init__(self, tester, id)
        self.name = "TestePlutoWriteRegisters"
        self.desc = "Pluto Modbus write registers default"
        self.expected_values = [0, 0]

    def test(self):
        read = []
        for add in [2,5]:
            reg = self.tester.plutoGateway.read_holding_registers(1, add, 1)
            read.append(reg[0])
        print(read)

        for n in range(1):
            self.step(("Read number %d/1:" % (n + 1)))
            self.sleep(0.134)
            for i, reg in enumerate(read):
                if reg != self.expected_values[i]:
                        self.step(("Digital Register %d doesn't match in expected value (%d) : %d " % (
                        i, self.expected_values[i], reg)))
                        return False

        self.step("Pluto write modbus registers default values as expected")
        return True


class TestPermitsValvesBoot(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestPermitsValvesBoot"
        self.desc = "Check if all permits are off when the PLC is powered"

    def test(self):
        self.step(self.desc)

        for port in ["Q0","Q1","Q2","Q3","Q4","Q5","IQ20","IQ21","IQ22","IQ23"]:
            if self.tester.testBox.read_port("plc",port) > 0.5:
                self.step("PLC output %s is not off."%port)
                return False

        for ch in ["HVStat","CVStat","VcrPumpPerm","VhxPumpPerm","MainVcrVcc","MainVhxVcc","VcrVcc01","VcrVcc02","VcrVcc03","VcrVcc04"]:
            if self.tester.plutoGateway.read_ch(ch) != 0:
                self.step("Pluto modbus indicator for %s is not off."%ch)
                return False


        self.step("Success message")
        return True


class TestChannelsBootDefault(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestChannelsBootDefault"
        self.desc = "Check if all channels are as expected when the PLC is powered"

    def test(self):
        self.step(self.desc)

        self.step("Checking boot default values.")
        chs = []
        for ch in self.tester.testBox.plc.channels:
            if ch.boot_value != "":
                chs.append((ch, ch.boot_value))
        for ch in self.tester.plutoGateway.channels:
            if ch.boot_value != "":
                chs.append((ch, ch.boot_value))

        try:
            if self.checkChannels(chs):
                self.step("Boot default values Ok.")
                return True
        except:
            pass

        self.step("Boot values do not match defaults.")
        return False


class TestNormalValuesBoot(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestNotmalValuesBoot"
        self.desc = ""

    def test(self):
        self.step(self.desc)

        self.step("Checking boot default values.")
        chs = []
        for ch in self.tester.testBox.plc.channels:
            if str(ch.boot_value) != "":
                ch.write(ch.default_value)

        self.sleep(1)



        for port in ["Q0","Q1","Q2","Q3","Q4","Q5","IQ20","IQ21","IQ22","IQ23"]:
            if self.tester.testBox.read_port("plc",port) > 0.5:
                self.step("PLC output %s is not off."%port)
                return False

        for ch in ["HVStat","CVStat","VcrPumpPerm","VhxPumpPerm","MainVcrVcc","MainVhxVcc","VcrVcc01","VcrVcc02","VcrVcc03","VcrVcc04"]:
            if self.tester.plutoGateway.read_ch(ch) != 0:
                self.step("Pluto modbus indicator for %s is not off."%ch)
                return False


        self.step("Success message")
        return True


class TestPlutoWriteReadback(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestePlutoWriteReadback"
        self.desc = "Test write and rbv Pluto adds"

    def test(self):
        self.step(self.desc)

        plutoGateway = self.tester.plutoGateway.dict

        for ch in plutoGateway.keys():

            if plutoGateway[ch]["permissions"] == "RW":

                ch_rbv = ch.replace("_w","")
                sleep=0.1

                self.step("Testing %s (%s) and %s (%s)."%(ch,"%d:%d.%d"%(plutoGateway[ch]["unitId"],plutoGateway[ch]["addr"],plutoGateway[ch]["bit"]),ch_rbv,"%d:%d.%d"%(plutoGateway[ch_rbv]["unitId"],plutoGateway[ch_rbv]["addr"],plutoGateway[ch_rbv]["bit"])))


                original_write = self.tester.plutoGateway.read_ch(ch)
                read = self.tester.plutoGateway.read_ch( ch_rbv)
                if original_write != read:
                    self.step("Failed on %s (%s) and %s (%s)." % (
                    ch, "%d:%d.%d" % (plutoGateway[ch]["unitId"], plutoGateway[ch]["addr"], plutoGateway[ch]["bit"]),
                    ch_rbv, "%d:%d.%d" % (
                    plutoGateway[ch_rbv]["unitId"], plutoGateway[ch_rbv]["addr"], plutoGateway[ch_rbv]["bit"])))
                    return False

                write = 1
                self.tester.plutoGateway.write_ch( ch,write)
                self.sleep(sleep)
                read = self.tester.plutoGateway.read_ch( ch_rbv)
                if write != read:
                    self.step("Failed on %s (%s) and %s (%s)." % (
                    ch, "%d:%d.%d" % (plutoGateway[ch]["unitId"], plutoGateway[ch]["addr"], plutoGateway[ch]["bit"]),
                    ch_rbv, "%d:%d.%d" % (
                    plutoGateway[ch_rbv]["unitId"], plutoGateway[ch_rbv]["addr"], plutoGateway[ch_rbv]["bit"])))
                    return False

                write = 0
                self.tester.plutoGateway.write_ch( ch,write)
                self.sleep(sleep)
                read = self.tester.plutoGateway.read_ch( ch_rbv)
                if write != read:
                    self.step("Failed on %s (%s) and %s (%s)." % (
                    ch, "%d:%d.%d" % (plutoGateway[ch]["unitId"], plutoGateway[ch]["addr"], plutoGateway[ch]["bit"]),
                    ch_rbv, "%d:%d.%d" % (
                    plutoGateway[ch_rbv]["unitId"], plutoGateway[ch_rbv]["addr"], plutoGateway[ch_rbv]["bit"])))
                    return False

                write = 1
                self.tester.plutoGateway.write_ch( ch,write)
                self.sleep(sleep)
                read = self.tester.plutoGateway.read_ch( ch_rbv)
                if write != read:
                    self.step("Failed on %s (%s) and %s (%s)." % (
                    ch, "%d:%d.%d" % (plutoGateway[ch]["unitId"], plutoGateway[ch]["addr"], plutoGateway[ch]["bit"]),
                    ch_rbv, "%d:%d.%d" % (
                    plutoGateway[ch_rbv]["unitId"], plutoGateway[ch_rbv]["addr"], plutoGateway[ch_rbv]["bit"])))
                    return False

                write = original_write
                self.tester.plutoGateway.write_ch( ch,write)
                self.sleep(sleep)
                read = self.tester.plutoGateway.read_ch( ch_rbv)
                if write != read:
                    self.step("Failed on %s (%s) and %s (%s)." % (
                    ch, "%d:%d.%d" % (plutoGateway[ch]["unitId"], plutoGateway[ch]["addr"], plutoGateway[ch]["bit"]),
                    ch_rbv, "%d:%d.%d" % (
                    plutoGateway[ch_rbv]["unitId"], plutoGateway[ch_rbv]["addr"], plutoGateway[ch_rbv]["bit"])))
                    return False



        self.step("All write adds are connected with the respective readback values addrs")
        return True


class TestAnalogScaling(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestAnalogScaling"
        self.desc = "Check the analog input wiring, linearity and scaling factors and offsets"

        #[P2.IA0,P2.IA1,P2.IA2,P2.IA3,P3.IA0,P3.IA1,P3.IA2,P3.IA3,]


        self.expected_factors=[2,2,2,2,2,1000,1000]
        self.expected_offsets=[0,0,0,0,0,0,0]

        self.n_points = 10

    def test(self):
        self.step(self.desc)
        self.step("Scaning...")

        test = dict()

        for n, port in enumerate(["IA0","IA1","IA2","IA3","IA4","IA6","IA7"]):

            test[port] = dict()
            test[port]["step"] = random.uniform(0.6, 1.6)
            test[port]["value"] = 0.05
            test[port]["value_array"] = []
            test[port]["finished"] = False

            for md in self.tester.testBox.dict[port]["modbus"]:
                if md.find("Voltage")>0:
                    test[port]["channel_voltage"] = md
                    test[port]["channel_voltage_array"] = []
                elif md.find("Valid")>0:
                    test[port]["channel_valid"] = md
                    test[port]["channel_valid_array"] = []
                else:
                    test[port]["channel_scaled"] = md
                    test[port]["channel_scaled_array"] = []

        cont = True
        while cont:
            cont = False
            for port in test.keys():
                if test[port]["value"]<10:

                    voltage = test[port]["value"] + test[port]["step"]
                    if voltage>10.1:
                        voltage =10.1
                    self.tester.testBox.write_port("plc", port, voltage)
                    test[port]["value"] = voltage
                    test[port]["value_array"].append(voltage)
                else:
                    test[port]["finished"] = True


            self.sleep(.7)

            for port in test.keys():
                if test[port]["finished"] is not True:
                    test[port]["channel_voltage_array"].append(self.tester.plutoGateway.read_ch( test[port]["channel_voltage"]))
                    test[port]["channel_scaled_array"].append(self.tester.plutoGateway.read_ch(test[port]["channel_scaled"]))
                    test[port]["channel_valid_array"].append(self.tester.plutoGateway.read_ch(test[port]["channel_valid"]))




                cont = cont | (test[port]["value"]<10.0)

        from scipy import stats

        self.step("Evaluating Valid")
        for port in test.keys():
            if sum(test[port]["channel_valid_array"]) != len(test[port]["channel_valid_array"]):
                self.step("Channel %s read not valid"%port)
                return False

        self.step("Evaluating Correct wiring")
        for port in test.keys():
            y = test[port]["value_array"]
            x = range(len(test[port]["channel_voltage_array"]))
            values=stats.linregress(x,y)

            y = test[port]["channel_voltage_array"]
            x = range(len(test[port]["channel_voltage_array"]))
            voltage=stats.linregress(x,y)



            if values.rvalue < 0.99 or voltage.rvalue<0.99:
                self.step("R-square too high on %s" % port)
                return False

            if abs(values.slope*1000-voltage.slope)>(values.slope*1000+voltage.slope)/2*0.005:
                self.step("Slope (over time) discrepancy between input and read value on %s. Probably wrong wiring." % port)
                return False

            if abs(values.intercept*1000 -voltage.intercept )>10000*0.002:
                self.step("Intercept  (over time) discrepancy between input and read value on %s. Probably wrong wiring." % port)
                return False


        self.step("Evaluating voltage linearity")
        for port in test.keys():
            y = test[port]["channel_voltage_array"]
            x = test[port]["value_array"]
            values=stats.linregress(x,y)

            if values.rvalue < 0.99:
                self.step("R-square too high on %s" % port)
                return False

            if abs(values.slope-1000)>1000*0.005:
                self.step("Transfer function Slope not 10 000 +- 0.5%% on %s." % port)
                return False

            if abs(values.intercept)>10000*0.005:
                self.step("Transfer function Intercept not 0 +- 0.5%% on %s." % port)
                return False


        self.step("Evaluating scaling coeficients")
        for port in test.keys():
            y = test[port]["channel_scaled_array"]
            x = test[port]["channel_voltage_array"]
            values = stats.linregress(x, y)

            print(values)

            if values.rvalue < 0.99:
                self.step("R-square too high on %s" % port)
                return False

            if abs(values.slope-1)>1*0.005:
                self.step("Scaling function Slope not 1 +- 0.5%% on %s." % port)
                return False

            if abs(values.intercept)>10000*0.005:
                self.step("Scaling function Intercept not 0 +- 0.5%% on %s." % port)
                return False

        self.step("Analog input wiring, linearity and scaling factors and offsets OK")
        return True


'''class TestCoolantValve(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestCoolantValve"
        self.desc = "Test TestCoolantValve permit logic"

    def test(self):
            self.step(self.desc)

            noLeakPort = self.tester.testBox.plc.P1.I4
            noLeak = self.tester.plutoGateway.P1_NoLeak
            leakFilter = self.tester.plutoGateway.P1_LeakFilter
            leakOkLatch = self.tester.plutoGateway.P1_LeakOkLatch
            leakOkLatchStatus = self.tester.plutoGateway.P1_LeakOkLatchStatus


            noLeakFaultPort = self.tester.testBox.plc.P1.I5
            noLeakFault = self.tester.plutoGateway.P1_NotLeakFault
            leakFaultFilter = self.tester.plutoGateway.P1_LeakFaultFilter
            leakFaultOkLatch = self.tester.plutoGateway.P1_LeakFaultOkLatch
            leakFaultOkLatchStatus = self.tester.plutoGateway.P1_LeakFaultOkLatchStatus

            leakIndicator = self.tester.testBox.plc.P1.Q13

            resetLeak_w = self.tester.plutoGateway.P1_ResetLeak_w

            masterResetPort = self.tester.testBox.plc.P2.I7
            masterReset = self.tester.plutoGateway.P2_MasterResetButton

            valvePort = self.tester.testBox.plc.P1.Q2
            valve =  self.tester.plutoGateway.P1_CoolantValve

            noLeakPortValues = [0,1]
            noLeakFaultPortValues = [1,1]
            resetModes = [masterResetPort,resetLeak_w]


            self.setDefault()

            self.sleep(1)

            n = 0

            try:
                for noLeakPortValue in noLeakPortValues:
                    for noLeakFaultPortValue in noLeakFaultPortValues:
                        for reset in resetModes:
                            n=n+1
                            print("--------------------------------------------------------------------------")

                            if n<0:
                                continue

                            compare = self.readAllChannels()

                            noLeakPort.write(noLeakPortValue)
                            noLeakFaultPort.write(noLeakPortValue)
                            self.sleep(.6)

                            self.checkDuring([(valvePort, 1)], 8)


                            leakFilterValue = not noLeakPortValue
                            leakOkLatchValue = noLeakPortValue
                            leakOkLatchStatusValue = not noLeakPortValue

                            leakFaultFilterValue = not noLeakPortValue
                            leakFaultOkLatchValue = noLeakPortValue
                            leakFaultOkLatchStatusValue = not noLeakPortValue

                            leakIndicatorValue = leakOkLatchStatusValue or leakFaultOkLatchStatusValue

                            valvePortValue = leakFaultOkLatchValue and leakOkLatchValue
                            valveValue = leakFaultOkLatchValue and leakOkLatchValue


                            self.checkChange([(noLeakPort, noLeakPortValue),
                                              (noLeak, noLeakPortValue),

                                              (noLeakFaultPort,noLeakFaultPortValue),
                                              (noLeakFault,noLeakFaultPortValue),

                                              (leakFilter, leakFilterValue),
                                              (leakOkLatch, leakOkLatchValue),
                                              (leakOkLatchStatus, leakOkLatchStatusValue),

                                              (leakFaultFilter, leakFaultFilterValue),
                                              (leakFaultOkLatch, leakFaultOkLatchValue),
                                              (leakFaultOkLatchStatus, leakFaultOkLatchStatusValue),

                                              (leakIndicator,leakIndicatorValue ),

                                              (valvePort, valvePortValue),
                                              (valve, valveValue),

                                              ],2,compare)

                            compare = self.readAllChannels()
                            reset.press()
                            self.checkChange([], 1, compare)

                            if not noLeakPortValue:
                                noLeakPort.write(1)

                                self.checkChange([(noLeakPort, 1),
                                                  (noLeak, 1),

                                                  (leakFilter, 0),
                                                  (leakOkLatch, 0),
                                                  (leakOkLatchStatus, 2),

                                                  (leakIndicator, 2),

                                                  (valvePort, 0),
                                                  (valve, 0),

                                                  ], 1, compare)



                            if not noLeakFaultPortValue:
                                noLeakFaultPort.write(1)
                                self.checkChange([(noLeakFaultPort, 1),
                                                  (noLeakFaultPort, 1),

                                                  (leakFaultFilter, 0),
                                                  (leakFaultOkLatch, 0),
                                                  (leakFaultOkLatchStatus, 2),

                                                  (leakIndicator, 2),

                                                  (valvePort, 0),
                                                  (valve, 0),

                                                  ], 1, compare)


                            compare = self.readAllChannels()
                            reset.press()
                            self.checkChange([], 1, compare)

                            self.checkDefault()




                self.step("Coolant Valve logic correct.")
                return True

            except ValueError as e:
                print (n)
                self.step("Coolant Valve logic failed! Failed at %s. Error: %s "%(self.step_m,str(e)))
                return False
                
'''

#test defaults
# test analog scalings
#test mpm active
#test limits

class TestAcPermit(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestCoolantValve"
        self.desc = "Test TestCoolantValve permit logic"

    def test(self):
            self.step(self.desc)

            noLeakPort = self.tester.testBox.plc.P1.I4
            noLeak = self.tester.plutoGateway.P1_NoLeak
            leakFilter = self.tester.plutoGateway.P1_LeakFilter
            leakOkLatch = self.tester.plutoGateway.P1_LeakOkLatch
            leakOkLatchStatus = self.tester.plutoGateway.P1_LeakOkLatchStatus


            noLeakFaultPort = self.tester.testBox.plc.P1.I5
            noLeakFault = self.tester.plutoGateway.P1_NotLeakFault
            leakFaultFilter = self.tester.plutoGateway.P1_LeakFaultFilter
            leakFaultOkLatch = self.tester.plutoGateway.P1_LeakFaultOkLatch
            leakFaultOkLatchStatus = self.tester.plutoGateway.P1_LeakFaultOkLatchStatus

            leakIndicator = self.tester.testBox.plc.P1.Q13

            resetLeak_w = self.tester.plutoGateway.P1_ResetLeak_w

            noSmokePort = self.tester.testBox.plc.P1.I7
            noSmoke = self.tester.plutoGateway.P1_NoSmoke
            smokeFilter = self.tester.plutoGateway.P1_SmokekFilter
            smokeOkLatch = self.tester.plutoGateway.P1_SmokeOkLatch
            smokeOkLatchStatus = self.tester.plutoGateway.P1_SmokeOkLatchStatus


            noSmokeFaultPort = self.tester.testBox.plc.P2.I4
            noSmokeFault = self.tester.plutoGateway.P2_NoSmokeFault
            smokeFaultFilter = self.tester.plutoGateway.P1_SmokeFaultFilter
            smokeFaultOkLatch = self.tester.plutoGateway.P1_SmokeFaultOkLatch
            smokeFaultOkLatchStatus = self.tester.plutoGateway.P1_SmokeFaultOkLatchStatus

            smokeIndicator = self.tester.testBox.plc.P1.Q15

            resetSmoke_w = self.tester.plutoGateway.P1_ResetSmoke_w


            tmp0Port = self.tester.testBox.plc.P1.IA0
            tmp1Port = self.tester.testBox.plc.P1.IA1
            tmp2Port = self.tester.testBox.plc.P1.IA2
            tmp3Port = self.tester.testBox.plc.P1.IA3

            tmp0 = self.tester.plutoGateway.P1_Tsw0
            tmp1 = self.tester.plutoGateway.P1_Tsw1
            tmp2 = self.tester.plutoGateway.P1_Tsw2
            tmp3 = self.tester.plutoGateway.P1_Tsw3

            tempOk = self.tester.plutoGateway.P1_TempOk
            tempHighFilter = self.tester.plutoGateway.P1_TempHighFilter
            tempOkLatch = self.tester.plutoGateway.P1_TempOKLatch
            tempOkLatcStatus = self.tester.plutoGateway.P1_TempOKLatchStatus

            tempIndicator = self.tester.testBox.plc.P1.Q14

            resetTemp_w = self.tester.plutoGateway.P1_ResetTemp_w


            masterResetPort = self.tester.testBox.plc.P2.I7
            masterReset = self.tester.plutoGateway.P2_MasterResetButton

            valvePort = self.tester.testBox.plc.P1.Q2
            valve =  self.tester.plutoGateway.P1_CoolantValve

            utPermitPort = self.tester.testBox.plc.P1.Q0
            utPermitIndicator = self.tester.testBox.plc.P1.IQ16
            utPermit = self.tester.plutoGateway.P1_UtPowerPerm


            noLeakPortValues = [0,1]
            noLeakFaultPortValues = [1,1]

            noSmokePortValues = [0,1]
            noSmokeFaultPortValues = [1,1]

            tmp0PortValues = [0,1]
            tmp1PortValues = [0,1]
            tmp2PortValues = [0,1]
            tmp3PortValues = [0,1]

            resetModes = ["soft", "hard"]


            self.setDefault()

            self.sleep(1)

            n = 0

            try:
                for noLeakPortValue in noLeakPortValues:
                    for noLeakFaultPortValue in noLeakFaultPortValues:
                            for noSmokePortValue in noSmokePortValues:
                                for noSmokeFaultPortValue in noSmokeFaultPortValues:
                                        for tmp0PortValue in tmp0PortValues:
                                            for tmp1PortValue in tmp1PortValues:
                                                for tmp2PortValue in tmp2PortValues:
                                                    for tmp3PortValue in tmp3PortValues:
                                                        for resetMode in resetModes:

                                                            n=n+1
                                                            print("--------------------------------------------------------------------------")

                                                            if n<0:
                                                                continue

                                                            compare = self.readAllChannels()

                                                            noLeakPort.write(noLeakPortValue)
                                                            noLeakFaultPort.write(noLeakPortValue)
                                                            noSmokePort.write(noLeakPortValue)
                                                            noSmokeFaultPort.write(noLeakPortValue)
                                                            tmp0Port.write(tmp0PortValue)
                                                            tmp1Port.write(tmp1PortValue)
                                                            tmp2Port.write(tmp2PortValue)
                                                            tmp3Port.write(tmp3PortValue)
                                                            self.sleep(.6)

                                                            # nothing should change during 9 seconds
                                                            self.checkDuring([(valvePort, 1),
                                                                              (valve,1,),
                                                                              (utPermitPort,1),
                                                                              (utPermitIndicator,1),
                                                                              (utPermit,1)
                                                                              ], 8)


                                                            leakFilterValue = not noLeakPortValue
                                                            leakOkLatchValue = noLeakPortValue
                                                            leakOkLatchStatusValue = not noLeakPortValue

                                                            leakFaultFilterValue = not noLeakFaultPortValue
                                                            leakFaultOkLatchValue = noLeakFaultPortValue
                                                            leakFaultOkLatchStatusValue = not noLeakFaultPortValue

                                                            leakIndicatorValue = leakOkLatchStatusValue or leakFaultOkLatchStatusValue

                                                            smokeFilterValue = not noSmokePortValue
                                                            smokeOkLatchValue = noSmokePortValue
                                                            smokeOkLatchStatusValue = not noSmokePortValue

                                                            smokeFaultFilterValue = not noSmokeFaultPortValue
                                                            smokeFaultOkLatchValue = noSmokeFaultPortValue
                                                            smokeFaultOkLatchStatusValue = not noSmokeFaultPortValue

                                                            smokeIndicatorValue = smokeOkLatchStatusValue or smokeFaultOkLatchStatusValue


                                                            tempOkValue = (tmp0PortValue + tmp1PortValue + tmp2PortValue + tmp3PortValue) >= 3
                                                            tempHighFilterValue = not tempOkValue
                                                            tempOkLatchValue = tempOkValue
                                                            tempOkLatcStatusValue = not tempOkValue

                                                            tempIndicatorValue = tempOkLatcStatusValue

                                                            valvePortValue = leakFaultOkLatchValue and leakOkLatchValue
                                                            valveValue = leakFaultOkLatchValue and leakOkLatchValue

                                                            utPermitPortValue = tempOkLatchValue and leakFaultOkLatchValue and leakOkLatchValue and smokeFaultOkLatchValue and smokeOkLatchValue
                                                            utPermitIndicatorValue = utPermitPortValue
                                                            utPermitValue = utPermitPortValue

                                                            self.pressChannels([resetTemp_w.press(), resetLeak_w.press(), resetSmoke_w.press(), masterResetPort.press()])

                                                            self.checkChange([
                                                                            # Leak
                                                                              (noLeakPort, noLeakPortValue),
                                                                              (noLeak, noLeakPortValue),

                                                                              (noLeakFaultPort,noLeakFaultPortValue),
                                                                              (noLeakFault,noLeakFaultPortValue),

                                                                              (leakFilter, leakFilterValue),
                                                                              (leakOkLatch, leakOkLatchValue),
                                                                              (leakOkLatchStatus, leakOkLatchStatusValue),

                                                                              (leakFaultFilter, leakFaultFilterValue),
                                                                              (leakFaultOkLatch, leakFaultOkLatchValue),
                                                                              (leakFaultOkLatchStatus, leakFaultOkLatchStatusValue),

                                                                              (leakIndicator,leakIndicatorValue ),

                                                                            # Smoke
                                                                              (noSmokePort, noSmokePortValue),
                                                                              (noSmoke, noSmokePortValue),

                                                                              (noSmokeFaultPort, noSmokeFaultPortValue),
                                                                              (noSmokeFault, noSmokeFaultPortValue),

                                                                              (smokeFilter, smokeFilterValue),
                                                                              (smokeOkLatch, smokeOkLatchValue),
                                                                              (smokeOkLatchStatus,
                                                                               smokeOkLatchStatusValue),

                                                                              (smokeFaultFilter, smokeFaultFilterValue),
                                                                              (smokeFaultOkLatch, smokeFaultOkLatchValue),
                                                                              (smokeFaultOkLatchStatus,smokeFaultOkLatchStatusValue),

                                                                              (smokeIndicator, smokeIndicatorValue),

                                                                            # Temperature

                                                                              (tmp0Port,tmp0PortValue),
                                                                              (tmp1Port,tmp1PortValue),
                                                                              (tmp2Port,tmp2PortValue),
                                                                              (tmp3Port,tmp3PortValue),

                                                                              (tmp0 ,tmp0PortValue),
                                                                              (tmp1 ,tmp1PortValue),
                                                                              (tmp2 ,tmp2PortValue),
                                                                              (tmp3 ,tmp3PortValue),

                                                                              (tempOk ,tempOkValue),
                                                                              (tempHighFilter ,tempHighFilterValue),
                                                                              (tempOkLatch,tempOkLatchValue),
                                                                              (tempOkLatcStatus,tempOkLatcStatusValue),

                                                                              (tempIndicator,tempIndicatorValue),

                                                                            # Outputs

                                                                              (valvePort, valvePortValue),
                                                                              (valve, valveValue),
                                                                              (utPermitPort,utPermitPortValue),
                                                                              (utPermitIndicator,utPermitIndicatorValue),
                                                                              (utPermit,utPermitValue),

                                                                              ],2,compare)


                                                            resets=[]

                                                            if not noLeakPortValue:
                                                                noLeakPort.write(1)
                                                                self.checkChange([(noLeakPort, 1),
                                                                                  (noLeak, 1),

                                                                                  (leakFilter, 0),
                                                                                  (leakOkLatch, 0),
                                                                                  (leakOkLatchStatus, 2),

                                                                                  (leakIndicator, 2),

                                                                                  (valvePort, 0),
                                                                                  (valve, 0),
                                                                                  (utPermitPort, 0),
                                                                                  (utPermitIndicator, 0),
                                                                                  (utPermit, 0),

                                                                                  ], 1, compare)
                                                                resets.append(resetLeak_w)



                                                            if not noLeakFaultPortValue:
                                                                noLeakFaultPort.write(1)
                                                                self.checkChange([(noLeakFaultPort, 1),
                                                                                  (noLeakFault, 1),

                                                                                  (leakFaultFilter, 0),
                                                                                  (leakFaultOkLatch, 0),
                                                                                  (leakFaultOkLatchStatus, 2),

                                                                                  (leakIndicator, 2),

                                                                                  (valvePort, 0),
                                                                                  (valve, 0),
                                                                                  (utPermitPort, 0),
                                                                                  (utPermitIndicator, 0),
                                                                                  (utPermit, 0),

                                                                                  ], 1, compare)
                                                                resets.append(resetLeak_w)


                                                            if not noSmokePortValue:
                                                                noSmokePort.write(1)
                                                                self.checkChange([(noSmokePort, 1),
                                                                                  (noSmoke, 1),

                                                                                  (smokeFilter, 0),
                                                                                  (smokeOkLatch, 0),
                                                                                  (smokeOkLatchStatus, 2),

                                                                                  (smokeIndicator, 2),

                                                                                  (valvePort, 0),
                                                                                  (valve, 0),
                                                                                  (utPermitPort, 0),
                                                                                  (utPermitIndicator, 0),
                                                                                  (utPermit, 0),

                                                                                  ], 1, compare)
                                                                resets.append(resetSmoke_w)



                                                            if not noSmokeFaultPortValue:
                                                                noSmokeFaultPort.write(1)
                                                                self.checkChange([(noSmokeFaultPort, 1),
                                                                                  (noSmokeFault, 1),

                                                                                  (smokeFaultFilter, 0),
                                                                                  (smokeFaultOkLatch, 0),
                                                                                  (smokeFaultOkLatchStatus, 2),

                                                                                  (smokeIndicator, 2),

                                                                                  (valvePort, 0),
                                                                                  (valve, 0),
                                                                                  (utPermitPort, 0),
                                                                                  (utPermitIndicator, 0),
                                                                                  (utPermit, 0),

                                                                                  ], 1, compare)
                                                                resets.append(resetSmoke_w)

                                                            if not tempOkValue:
                                                                tmp0Port.write(1)
                                                                tmp1Port.write(1)
                                                                tmp2Port.write(1)
                                                                tmp3Port.write(1)
                                                                self.checkChange([(tmp0Port,1),
                                                                              (tmp1Port,1),
                                                                              (tmp2Port,1),
                                                                              (tmp3Port,1),

                                                                              (tmp0 ,1),
                                                                              (tmp1 ,1),
                                                                              (tmp2 ,1),
                                                                              (tmp3 ,1),

                                                                                  (tempOk, 1),
                                                                                  (tempHighFilter, 0),
                                                                                  (tempOkLatch, 0),
                                                                                  (tempOkLatcStatus,2),

                                                                                  (tempIndicator, 2),

                                                                                  (valvePort, 0),
                                                                                  (valve, 0),
                                                                                  (utPermitPort, 0),
                                                                                  (utPermitIndicator, 0),
                                                                                  (utPermit, 0),

                                                                                  ], 1, compare)

                                                                resets.append(resetTemp_w)


                                                            if len(resets)>0:
                                                                if resetMode == "hard":
                                                                    masterResetPort.press()
                                                                else:
                                                                    self.pressChannels(resets)

                                                            self.checkDefault()




                self.step("Coolant Valve logic correct.")
                return True

            except ValueError as e:
                print (n)
                self.step("Coolant Valve logic failed! Failed at %s. Error: %s "%(self.step_m,str(e)))
                return False


class TestColdPermits(Test):
    def __init__(self,tester,id):
        Test.__init__(self,tester,id)
        self.name = "TestCoolantValve"
        self.desc = "Test TestCoolantValve permit logic"

    def test(self):
            self.step(self.desc)


            tmp0Port = self.tester.testBox.plc.P2.IA0
            tmp1Port = self.tester.testBox.plc.P2.IA1
            tmp2Port = self.tester.testBox.plc.P2.IA2
            tmp3Port = self.tester.testBox.plc.P2.IA3

            tmp0Current = self.tester.plutoGateway.P2_ClpRtd0Current
            tmp1Current = self.tester.plutoGateway.P2_ClpRtd1Current
            tmp2Current = self.tester.plutoGateway.P2_ClpRtd2Current
            tmp3Current = self.tester.plutoGateway.P2_ClpRtd3Current

            tmp0Temp = self.tester.plutoGateway.P2_ClpRtd0Temp
            tmp1Temp = self.tester.plutoGateway.P2_ClpRtd1Temp
            tmp2Temp = self.tester.plutoGateway.P2_ClpRtd2Temp
            tmp3Temp = self.tester.plutoGateway.P2_ClpRtd3Temp

            tmp0Valid = self.tester.plutoGateway.P2_ClpRtd0Valid
            tmp1Valid = self.tester.plutoGateway.P2_ClpRtd1Valid
            tmp2Valid = self.tester.plutoGateway.P2_ClpRtd2Valid
            tmp3Valid = self.tester.plutoGateway.P2_ClpRtd3Valid

            tmp0NotLow = self.tester.plutoGateway.P2_ClpRtd0NotLow
            tmp1NotLow = self.tester.plutoGateway.P2_ClpRtd1NotLow
            tmp2NotLow = self.tester.plutoGateway.P2_ClpRtd2NotLow
            tmp3NotLow = self.tester.plutoGateway.P2_ClpRtd3NotLow

            tmp0NotHigh = self.tester.plutoGateway.P2_ClpRtd0NotHigh
            tmp1NotHigh = self.tester.plutoGateway.P2_ClpRtd1NotHigh
            tmp2NotHigh = self.tester.plutoGateway.P2_ClpRtd2NotHigh
            tmp3NotHigh = self.tester.plutoGateway.P2_ClpRtd3NotHigh

            tempNotHigh =  self.tester.plutoGateway.P2_ClpTempNotHigh
            tempHighFilter =  self.tester.plutoGateway.P2_ClpTempHighFilter
            tempHighLimit =  self.tester.plutoGateway.P2_ClpHighLimit

            tempHighOkLatch = self.tester.plutoGateway.P2_ClpTempHighOkLatch
            tempHighOkLatchStatus = self.tester.plutoGateway.P2_ClpTempHighOkLatchStatus
            hotLight = self.tester.plutoGateway.P2_ClpHotLight
            hotLightPort =  self.tester.testBox.plc.P2.IQ14

            resetTempHigh_w =  self.tester.plutoGateway.P2_ResetClpHigh_w

            heatPermitBlock = self.tester.plutoGateway.P2_ClpHeatPermBlock
            heatPermitBlockSet_w = self.tester.plutoGateway.P2_ClpHeatPermBlockSet_w
            heatPermitBlockReset_w = self.tester.plutoGateway.P2_ClpHeatPermBlockReset_w

            heatPermitLockLight = self.tester.plutoGateway.P2_ClpHeatLockLight
            heatPermitLockLightPort =  self.tester.testBox.plc.P2.IQ16
            heatPermit = self.tester.plutoGateway.P2_ClpHeatPerm
            heatPermitPort =  self.tester.testBox.plc.P2.Q0


            tempNotLow =  self.tester.plutoGateway.P2_ClpTempNotLow
            tempLowFilter =  self.tester.plutoGateway.P2_ClpTempLowFilter
            tempLowLimit =  self.tester.plutoGateway.P2_ClpLowLimit
            tempLowOkLatch = self.tester.plutoGateway.P2_ClpTempLowOkLatch
            tempLowOkLatchStatus = self.tester.plutoGateway.P2_ClpTempLowOkLatchStatus
            coldLight = self.tester.plutoGateway.P2_ClpColdLight
            coldLightPort =  self.tester.testBox.plc.P2.IQ15


            resetTempLow_w =  self.tester.plutoGateway.P2_ResetClpLow_w

            refPermitBlock = self.tester.plutoGateway.P2_ClpRefPermBlock
            refPermitBlockSet_w = self.tester.plutoGateway.P2_ClpRefPermBlockSet_w
            refPermitBlockReset_w = self.tester.plutoGateway.P2_ClpRefPermBlockReset_w

            refPermitLockLight = self.tester.plutoGateway.P2_ClpRefLockLight
            refPermitLockLightPort =  self.tester.testBox.plc.P2.IQ16
            refPermit = self.tester.plutoGateway.P2_ClpRefPerm
            refPermitPort =  self.tester.testBox.plc.P2.Q1


            hexVacOk = self.tester.plutoGateway.P3_HexVacOk
            hexVacOkPort = self.tester.testBox.plc.P3.IQ14
            hexVacOkLatch = self.tester.plutoGateway.P3_HexVacOkLatch
            hexVacLatchStatus = self.tester.plutoGateway.P3_HexVacOkLatchStatus
            hexVavBadLight = self.tester.plutoGateway.P3_HexVacBadLight
            hexVacReset_w = self.tester.plutoGateway.P3_ResetHexVac_w

            cryVacOk = self.tester.plutoGateway.P3_CryVacOk
            cryVacOkPort = self.tester.testBox.plc.P3.IQ15
            cryVacOkLatch = self.tester.plutoGateway.P3_CryVacOkLatch
            cryVacLatchStatus = self.tester.plutoGateway.P3_CryVacOkLatchStatus
            cryVavBadLight = self.tester.plutoGateway.P3_CryVacBadLight
            cryVacReset_w = self.tester.plutoGateway.P3_ResetCryVac_w



            masterResetPort = self.tester.testBox.plc.P2.I7
            masterReset = self.tester.plutoGateway.P2_MasterResetButton




            tmp0PortValues = [5,10,20]
            tmp1PortValues = [5,10,20]
            tmp2PortValues = [5,10,20]
            tmp3PortValues = [5,10,20]
            hexVacOkPortValues = [0,1]
            cryVacOkPortValues = [0,1]

            resetModes = ["soft", "hard"]


            self.setDefault()

            self.sleep(1)

            n = 0

            try:
                for tmp0PortValue in tmp0PortValues:
                    for tmp1PortValue in tmp1PortValues:
                        for tmp2PortValue in tmp2PortValues:
                            for tmp3PortValue in tmp3PortValues:
                                for resetMode in resetModes:
                                    for hexVacOkPortValue in hexVacOkPortValues:
                                        for cryVacOkPortValue in cryVacOkPortValues:

                                            n=n+1
                                            print("--------------------------------------------------------------------------")

                                            if n<0:
                                                continue

                                            compare = self.readAllChannels()

                                            tmp0Port.write(tmp0PortValue)
                                            tmp1Port.write(tmp1PortValue)
                                            tmp2Port.write(tmp2PortValue)
                                            tmp3Port.write(tmp3PortValue)
                                            hexVacOkPort.write(hexVacOkPortValue)
                                            cryVacOkPort.write(cryVacOkPortValue)
                                            self.sleep(.6)

                                            hexVacOkLatchValue = hexVacOkPortValue
                                            hexVacLatchStatusValue = not hexVacOkPortValue
                                            hexVavBadLightValue =  not hexVacOkPortValue

                                            cryVacOkLatchValue = cryVacOkPortValue
                                            cryVacLatchStatusValue = not cryVacOkPortValue
                                            cryVavBadLightValue = not cryVacOkPortValue

                                            lowLimit = 228
                                            tmp0NotLowValue = int(tmp0PortValue >lowLimit)
                                            tmp1NotLowValue = int(tmp1PortValue >lowLimit)
                                            tmp2NotLowValue = int(tmp2PortValue >lowLimit)
                                            tmp3NotLowValue = int(tmp3PortValue >lowLimit)

                                            highLimit = 295
                                            tmp0NotHighValue =int(tmp0PortValue < highLimit)
                                            tmp1NotHighValue =int(tmp1PortValue < highLimit)
                                            tmp2NotHighValue =int(tmp2PortValue < highLimit)
                                            tmp3NotHighValue =int(tmp3PortValue < highLimit)

                                            tempNotHighValue = int((int(tmp0NotHighValue) + int(tmp1NotHighValue) + int(tmp2NotHighValue) +int(tmp3NotHighValue)) >=3)
                                            tempHighFilter = not tempNotHighValue

                                            tempHighOKLatch = tempNotHighValue
                                            tempHighOkLatchStatusValue = not tempHighOKLatch
                                            hotLightValue = tempHighOkLatchStatusValue
                                            hotLightPortValue = tempHighOkLatchStatusValue

                                            heatPermitValue = tempNotHighValue
                                            heatPermitPortValue = heatPermitValue
                                            heatPermitLockLightValue = not heatPermitValue
                                            heatPermitLockLightPortValue =  not heatPermitValue

                                            tempNotLowValue = int((int(tmp0NotLowValue) + int(tmp1NotLowValue) + int(tmp2NotLowValue) +int(tmp3NotLowValue)) >=3)
                                            tempLowFilterValue = not tempNotLowValue

                                            tempLowOkLatchValue = tempNotLowValue
                                            tempLowOkLatchStatusValue = not tempLowOkLatchValue
                                            coldLightValue = tempLowOkLatchStatusValue
                                            coldLightPortValue = tempLowOkLatchStatusValue


                                            refPermitValue = hexVacOkPortValue and cryVacOkPortValue
                                            refPermitPortValue = refPermitValue
                                            refPermitLockLightValue = not refPermitValue
                                            refPermitLockLightPortValue = not refPermitValue

                                            refPermitValue10 = tempNotLowValue and hexVacOkPortValue and cryVacOkPortValue
                                            refPermitPortValue10 = refPermitValue
                                            refPermitLockLightValue10 = not refPermitValue
                                            refPermitLockLightPortValue10 = not refPermitValue


                                            # Should change imediatly
                                            self.checkChange([
                                                (tmp0Port, tmp0PortValue),
                                                (tmp1Port, tmp1PortValue),
                                                (tmp2Port, tmp2PortValue),
                                                (tmp3Port, tmp3PortValue),

                                                (tmp0Current, tmp0PortValue),
                                                (tmp1Current, tmp1PortValue),
                                                (tmp2Current, tmp2PortValue),
                                                (tmp3Current, tmp3PortValue),

                                                (tmp0Temp, tmp0PortValue),
                                                (tmp1Temp, tmp1PortValue),
                                                (tmp2Temp, tmp2PortValue),
                                                (tmp3Temp, tmp3PortValue),

                                                (hexVacOkPort,hexVacOkPortValue),
                                                (hexVacOk,hexVacOkPortValue),
                                                (hexVacOkLatch,hexVacOkLatchValue),
                                                (hexVacLatchStatus, hexVacLatchStatusValue),
                                                (hexVavBadLight,hexVavBadLightValue),

                                                (cryVacOkPort, cryVacOkPortValue),
                                                (cryVacOk, cryVacOkPortValue),
                                                (cryVacOkLatch,cryVacOkLatchValue),
                                                (cryVacLatchStatus,cryVacLatchStatusValue),
                                                (cryVavBadLight,cryVavBadLightValue),


                                                ( tmp0NotLow,tmp0NotLowValue ),
                                                (tmp1NotLow,     tmp1NotLowValue ),
                                                (tmp2NotLow,   tmp2NotLowValue),
                                                (tmp3NotLow,       tmp3NotLowValue),

                                                (tmp0NotHigh,       tmp0NotHighValue),
                                                (tmp1NotHigh,    tmp1NotHighValue),
                                                (tmp2NotHigh, tmp2NotHighValue),
                                                (tmp3NotHigh, tmp3NotHighValue),

                                                (tempNotHigh, tempNotHighValue),
                                                #(tempHighFilter,   tempHighFilter),

                                                #(tempHighOKLatch,  tempHighOKLatch),
                                                #(tempHighOkLatchStatus,   tempHighOkLatchStatusValue),
                                                #(hotLight,  hotLightValue),
                                                #(hotLightPort,   hotLightPortValue),
                                                #(heatPermit,   heatPermitValue),
                                                #(heatPermitPort,   heatPermitPortValue),
                                                #(heatPermitLockLight,   heatPermitLockLightValue),
                                                #(heatPermitLockLightPort, heatPermitLockLightPortValue),

                                                (tempNotLow, tempNotLowValue),
                                                #(tempLowFilter,  tempLowFilterValue),
                                                #(tempLowOkLatch,  tempLowOkLatchValue),
                                                #(tempLowOkLatchStatus,  tempLowOkLatchStatusValue),
                                                #(coldLight,  coldLightValue),
                                                #(coldLightPort, coldLightPortValue),

                                                (refPermit,  refPermitValue),
                                                (refPermitPort, refPermitPortValue),
                                                (refPermitLockLight, refPermitLockLightValue),
                                                (refPermitLockLightPort, refPermitLockLightPortValue),


                                                ], 2, compare)


                                            # nothing should change during 9 seconds
                                            self.checkDuring([(refPermitPort, 1),
                                                              (refPermit,1,),
                                                              (heatPermitPort,refPermitPortValue),
                                                              (heatPermit,refPermitValue),
                                                              ], 8)




                                            self.pressChannels([resetTemp_w.press(), resetLeak_w.press(), resetSmoke_w.press(), masterResetPort.press()])

                                            self.checkChange([
                                                (tmp0Port, tmp0PortValue),
                                                (tmp1Port, tmp1PortValue),
                                                (tmp2Port, tmp2PortValue),
                                                (tmp3Port, tmp3PortValue),

                                                (tmp0Current, tmp0PortValue),
                                                (tmp1Current, tmp1PortValue),
                                                (tmp2Current, tmp2PortValue),
                                                (tmp3Current, tmp3PortValue),

                                                (tmp0Temp, tmp0PortValue),
                                                (tmp1Temp, tmp1PortValue),
                                                (tmp2Temp, tmp2PortValue),
                                                (tmp3Temp, tmp3PortValue),

                                                (hexVacOkPort,hexVacOkPortValue),
                                                (hexVacOk,hexVacOkPortValue),
                                                (hexVacOkLatch,hexVacOkLatchValue),
                                                (hexVacLatchStatus, hexVacLatchStatusValue),
                                                (hexVavBadLight,hexVavBadLightValue),

                                                (cryVacOkPort, cryVacOkPortValue),
                                                (cryVacOk, cryVacOkPortValue),
                                                (cryVacOkLatch,cryVacOkLatchValue),
                                                (cryVacLatchStatus,cryVacLatchStatusValue),
                                                (cryVavBadLight,cryVavBadLightValue),


                                                ( tmp0NotLow,tmp0NotLowValue ),
                                                (tmp1NotLow,     tmp1NotLowValue ),
                                                (tmp2NotLow,   tmp2NotLowValue),
                                                (tmp3NotLow,       tmp3NotLowValue),

                                                (tmp0NotHigh, tmp0NotHighValue),
                                                (tmp1NotHigh, tmp1NotHighValue),
                                                (tmp2NotHigh, tmp2NotHighValue),
                                                (tmp3NotHigh, tmp3NotHighValue),

                                                (tempNotHigh, tempNotHighValue),
                                                (tempHighFilter,   tempHighFilter),

                                                (tempHighOKLatch,  tempHighOKLatch),
                                                (tempHighOkLatchStatus,   tempHighOkLatchStatusValue),
                                                (hotLight,  hotLightValue),
                                                (hotLightPort,   hotLightPortValue),
                                                (heatPermit,   heatPermitValue),
                                                (heatPermitPort,   heatPermitPortValue),
                                                (heatPermitLockLight,   heatPermitLockLightValue),
                                                (heatPermitLockLightPort, heatPermitLockLightPortValue),

                                                (tempNotLow, tempNotLowValue),
                                                (tempLowFilter,  tempLowFilterValue),
                                                (tempLowOkLatch,  tempLowOkLatchValue),
                                                (tempLowOkLatchStatus,  tempLowOkLatchStatusValue),
                                                (coldLight,  coldLightValue),
                                                (coldLightPort, coldLightPortValue),

                                                (refPermit,  refPermitValue10),
                                                (refPermitPort, refPermitPortValue10),
                                                (refPermitLockLight, refPermitLockLightValue10),
                                                (refPermitLockLightPort, refPermitLockLightPortValue10),


                                                ], 2, compare)


                                            resets=[]

                                            if not noLeakPortValue:
                                                noLeakPort.write(1)
                                                self.checkChange([(noLeakPort, 1),
                                                                  (noLeak, 1),

                                                                  (leakFilter, 0),
                                                                  (leakOkLatch, 0),
                                                                  (leakOkLatchStatus, 2),

                                                                  (leakIndicator, 2),

                                                                  (valvePort, 0),
                                                                  (valve, 0),
                                                                  (utPermitPort, 0),
                                                                  (utPermitIndicator, 0),
                                                                  (utPermit, 0),

                                                                  ], 1, compare)
                                                resets.append(resetLeak_w)



                                            if not noLeakFaultPortValue:
                                                noLeakFaultPort.write(1)
                                                self.checkChange([(noLeakFaultPort, 1),
                                                                  (noLeakFault, 1),

                                                                  (leakFaultFilter, 0),
                                                                  (leakFaultOkLatch, 0),
                                                                  (leakFaultOkLatchStatus, 2),

                                                                  (leakIndicator, 2),

                                                                  (valvePort, 0),
                                                                  (valve, 0),
                                                                  (utPermitPort, 0),
                                                                  (utPermitIndicator, 0),
                                                                  (utPermit, 0),

                                                                  ], 1, compare)
                                                resets.append(resetLeak_w)


                                            if not noSmokePortValue:
                                                noSmokePort.write(1)
                                                self.checkChange([(noSmokePort, 1),
                                                                  (noSmoke, 1),

                                                                  (smokeFilter, 0),
                                                                  (smokeOkLatch, 0),
                                                                  (smokeOkLatchStatus, 2),

                                                                  (smokeIndicator, 2),

                                                                  (valvePort, 0),
                                                                  (valve, 0),
                                                                  (utPermitPort, 0),
                                                                  (utPermitIndicator, 0),
                                                                  (utPermit, 0),

                                                                  ], 1, compare)
                                                resets.append(resetSmoke_w)



                                            if not noSmokeFaultPortValue:
                                                noSmokeFaultPort.write(1)
                                                self.checkChange([(noSmokeFaultPort, 1),
                                                                  (noSmokeFault, 1),

                                                                  (smokeFaultFilter, 0),
                                                                  (smokeFaultOkLatch, 0),
                                                                  (smokeFaultOkLatchStatus, 2),

                                                                  (smokeIndicator, 2),

                                                                  (valvePort, 0),
                                                                  (valve, 0),
                                                                  (utPermitPort, 0),
                                                                  (utPermitIndicator, 0),
                                                                  (utPermit, 0),

                                                                  ], 1, compare)
                                                resets.append(resetSmoke_w)

                                            if not tempOkValue:
                                                tmp0Port.write(1)
                                                tmp1Port.write(1)
                                                tmp2Port.write(1)
                                                tmp3Port.write(1)
                                                self.checkChange([(tmp0Port,1),
                                                              (tmp1Port,1),
                                                              (tmp2Port,1),
                                                              (tmp3Port,1),

                                                              (tmp0 ,1),
                                                              (tmp1 ,1),
                                                              (tmp2 ,1),
                                                              (tmp3 ,1),

                                                                  (tempOk, 1),
                                                                  (tempHighFilter, 0),
                                                                  (tempOkLatch, 0),
                                                                  (tempOkLatcStatus,2),

                                                                  (tempIndicator, 2),

                                                                  (valvePort, 0),
                                                                  (valve, 0),
                                                                  (utPermitPort, 0),
                                                                  (utPermitIndicator, 0),
                                                                  (utPermit, 0),

                                                                  ], 1, compare)

                                                resets.append(resetTemp_w)


                                            if len(resets)>0:
                                                if resetMode == "hard":
                                                    masterResetPort.press()
                                                else:
                                                    self.pressChannels(resets)

                                            self.checkDefault()




                self.step("Coolant Valve logic correct.")
                return True

            except ValueError as e:
                print (n)
                self.step("Coolant Valve logic failed! Failed at %s. Error: %s "%(self.step_m,str(e)))
                return False