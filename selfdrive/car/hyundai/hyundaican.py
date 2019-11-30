import crcmod
from selfdrive.car.hyundai.values import CAR, CHECKSUM

hyundai_checksum = crcmod.mkCrcFun(0x11D, initCrc=0xFD, rev=False, xorOut=0xdf)

def make_can_msg(addr, dat, alt):
  return [addr, 0, dat, alt]

def create_lkas11(packer, car_fingerprint, apply_steer, steer_req, cnt, enabled, lkas11, hud_alert,
                                   lane_visible, left_lane_depart, right_lane_depart, keep_stock=False):
  values = {
    "CF_Lkas_Bca_R": 3 if enabled else 0,
    "CF_Lkas_LdwsSysState": lane_visible,
    "CF_Lkas_SysWarning": hud_alert,
    "CF_Lkas_LdwsLHWarning": left_lane_depart,
    "CF_Lkas_LdwsRHWarning": right_lane_depart,
    "CF_Lkas_HbaLamp": lkas11["CF_Lkas_HbaLamp"] if keep_stock else 0,
    "CF_Lkas_FcwBasReq": lkas11["CF_Lkas_FcwBasReq"] if keep_stock else 0,
    "CR_Lkas_StrToqReq": apply_steer,
    "CF_Lkas_ActToi": steer_req,
    "CF_Lkas_ToiFlt": 0,
    "CF_Lkas_HbaSysState": lkas11["CF_Lkas_HbaSysState"] if keep_stock else 1,
    "CF_Lkas_FcwOpt": lkas11["CF_Lkas_FcwOpt"] if keep_stock else 0,
    "CF_Lkas_HbaOpt": lkas11["CF_Lkas_HbaOpt"] if keep_stock else 3,
    "CF_Lkas_MsgCount": cnt,
    "CF_Lkas_FcwSysState": lkas11["CF_Lkas_FcwSysState"] if keep_stock else 0,
    "CF_Lkas_FcwCollisionWarning": lkas11["CF_Lkas_FcwCollisionWarning"] if keep_stock else 0,
    "CF_Lkas_FusionState": lkas11["CF_Lkas_FusionState"] if keep_stock else 0,
    "CF_Lkas_Chksum": 0,
    "CF_Lkas_FcwOpt_USM": 2 if enabled else 1,
    "CF_Lkas_LdwsOpt_USM": lkas11["CF_Lkas_LdwsOpt_USM"] if keep_stock else 3,
  }

  if car_fingerprint == CAR.GENESIS:
    values["CF_Lkas_Bca_R"] = 2
    values["CF_Lkas_HbaSysState"] = lkas11["CF_Lkas_HbaSysState"] if keep_stock else 0
    values["CF_Lkas_HbaOpt"] = lkas11["CF_Lkas_HbaOpt"] if keep_stock else 1
    values["CF_Lkas_FcwOpt_USM"] = lkas11["CF_Lkas_FcwOpt_USM"] if keep_stock else 2
    values["CF_Lkas_LdwsOpt_USM"] = lkas11["CF_Lkas_LdwsOpt_USM"] if keep_stock else 0
  if car_fingerprint == CAR.KIA_OPTIMA:
    values["CF_Lkas_Bca_R"] = 0
    values["CF_Lkas_HbaOpt"] = lkas11["CF_Lkas_HbaOpt"] if keep_stock else 1
    values["CF_Lkas_FcwOpt_USM"] = lkas11["CF_Lkas_FcwOpt_USM"] if keep_stock else 0
    
  dat = packer.make_can_msg("LKAS11", 0, values)[2]

  if car_fingerprint in CHECKSUM["crc8"]:
    # CRC Checksum as seen on 2019 Hyundai Santa Fe
    dat = dat[:6] + dat[7:8]
    checksum = hyundai_checksum(dat)
  elif car_fingerprint in CHECKSUM["6B"]:
    # Checksum of first 6 Bytes, as seen on 2018 Kia Sorento
    checksum = sum(dat[:6]) % 256
  else:
    # Checksum of first 6 Bytes and last Byte as seen on 2018 Kia Stinger
    checksum = (sum(dat[:6]) + dat[7]) % 256

  values["CF_Lkas_Chksum"] = checksum

  return packer.make_can_msg("LKAS11", 0, values)

def create_lkas12():
  return make_can_msg(1342, b"\x00\x00\x00\x00\x60\x05", 0)


def create_1191():
  return make_can_msg(1191, b"\x01\x00", 0)


def create_1156():
  return make_can_msg(1156, b"\x08\x20\xfe\x3f\x00\xe0\xfd\x3f", 0)

def create_clu11(packer, clu11, button, cnt):
  values = {
    "CF_Clu_CruiseSwState": button,
    "CF_Clu_CruiseSwMain": clu11["CF_Clu_CruiseSwMain"],
    "CF_Clu_SldMainSW": clu11["CF_Clu_SldMainSW"],
    "CF_Clu_ParityBit1": clu11["CF_Clu_ParityBit1"],
    "CF_Clu_VanzDecimal": clu11["CF_Clu_VanzDecimal"],
    "CF_Clu_Vanz": clu11["CF_Clu_Vanz"],
    "CF_Clu_SPEED_UNIT": clu11["CF_Clu_SPEED_UNIT"],
    "CF_Clu_DetentOut": clu11["CF_Clu_DetentOut"],
    "CF_Clu_RheostatLevel": clu11["CF_Clu_RheostatLevel"],
    "CF_Clu_CluInfo": clu11["CF_Clu_CluInfo"],
    "CF_Clu_AmpInfo": clu11["CF_Clu_AmpInfo"],
    "CF_Clu_AliveCnt1": cnt,
  }

  return packer.make_can_msg("CLU11", 0, values)

def create_scc12(packer, cnt, scc12):
  values = {
    "CF_VSM_Prefill": scc12["CF_VSM_Prefill"],
    "CF_VSM_DecCmdAct": scc12["CF_VSM_DecCmdAct"],
    "CF_VSM_HBACmd": scc12["CF_VSM_HBACmd"],
    "CF_VSM_Warn": scc12["CF_VSM_Warn"],
    "CF_VSM_Stat": scc12["CF_VSM_Stat"],
    "CF_VSM_BeltCmd": scc12["CF_VSM_BeltCmd"],
    "ACCFailInfo": scc12["ACCFailInfo"],
    "ACCMode": scc12["ACCMode"],
    "StopReq": scc12["StopReq"],
    "CR_VSM_DecCmd": scc12["CR_VSM_DecCmd"],
    "aReqMax": scc12["aReqMax"],
    "TakeOverReq": scc12["TakeOverReq"],
    "PreFill": scc12["PreFill"],
    "aReqMin": scc12["aReqMin"],
    "CF_VSM_ConfMode": scc12["CF_VSM_ConfMode"],
    "AEB_Failinfo": scc12["AEB_Failinfo"],
    "AEB_Status": scc12["AEB_Status"],
    "AEB_CmdAct": scc12["AEB_CmdAct"],
    "AEB_StopReq": scc12["AEB_StopReq"],
    "CR_VSM_Alive": cnt,
    "CR_VSM_ChkSum": 0,
  }

  dat = packer.make_can_msg("SCC12", 0, values)[2]
  values["CR_VSM_ChkSum"] = 16 - sum([sum(divmod(i, 16)) for i in dat]) % 16

  return packer.make_can_msg("SCC12", 0, values)

def create_scc11(packer, cnt, scc11):
  values = {
    "MainMode_ACC": scc11["MainMode_ACC"],
    "SCCInfoDisplay": scc11["SCCInfoDisplay"],
    "AliveCounterACC": cnt,
    "VSetDis": scc11["VSetDis"],
    "ObjValid": scc11["ObjValid"],
    "DriverAlertDisplay": scc11["DriverAlertDisplay"],
    "TauGapSet": scc11["TauGapSet"],
    "ACC_ObjStatus": scc11["ACC_ObjStatus"],
    "ACC_ObjLatPos": scc11["ACC_ObjLatPos"],
    "ACC_ObjDist": scc11["ACC_ObjDist"],
    "ACC_ObjRelSpd": scc11["ACC_ObjRelSpd"],
    "Navi_SCC_Curve_Status": scc11["Navi_SCC_Curve_Status"],
    "Navi_SCC_Curve_Act": scc11["Navi_SCC_Curve_Act"],
    "Navi_SCC_Camera_Act": scc11["Navi_SCC_Camera_Act"],
    "Navi_SCC_Camera_Status": scc11["Navi_SCC_Camera_Status"],
   }
  return packer.make_can_msg("scc11", 0, values)

def create_mdps12(packer, car_fingerprint, cnt, mdps12):
  values = {
    "CR_Mdps_StrColTq": mdps12["CR_Mdps_StrColTq"],
    "CF_Mdps_Def": mdps12["CF_Mdps_Def"],
    "CF_Mdps_ToiActive": 0,
    "CF_Mdps_ToiUnavail": 1,
    "CF_Mdps_MsgCount2": cnt,
    "CF_Mdps_Chksum2": 0,
    "CF_Mdps_ToiFlt": mdps12["CF_Mdps_ToiFlt"],
    "CF_Mdps_SErr": mdps12["CF_Mdps_SErr"],
    "CR_Mdps_StrTq": mdps12["CR_Mdps_StrTq"],
    "CF_Mdps_FailStat": mdps12["CF_Mdps_FailStat"],
    "CR_Mdps_OutTq": mdps12["CR_Mdps_OutTq"],
  }

  dat = packer.make_can_msg("MDPS12", 2, values)[2]
  checksum = sum(dat) % 256
  values["CF_Mdps_Chksum2"] = checksum

  return packer.make_can_msg("MDPS12", 2, values)
