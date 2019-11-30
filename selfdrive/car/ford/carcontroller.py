from cereal import car
from selfdrive.car.ford.fordcan import make_can_msg, create_steer_command, create_lkas_ui, \
                                       spam_cancel_button
from selfdrive.can.packer import CANPacker


MAX_STEER_DELTA = 1
TOGGLE_DEBUG = False

class CarController():
  def __init__(self, dbc_name, enable_camera, vehicle_model):
    self.packer = CANPacker(dbc_name)
    self.enable_camera = enable_camera
    self.enabled_last = False
    self.main_on_last = False
    self.vehicle_model = vehicle_model
    self.generic_toggle_last = 0
    self.steer_alert_last = False
    self.lkas_action = 0

  def update(self, enabled, CS, frame, actuators, visual_alert, pcm_cancel):

    can_sends = []
    steer_alert = visual_alert == car.CarControl.HUDControl.VisualAlert.steerRequired

    apply_steer = actuators.steer

    if self.enable_camera:

      if pcm_cancel:
        #print "CANCELING!!!!"
        can_sends.append(spam_cancel_button(self.packer))

      if (frame % 3) == 0:

        curvature = self.vehicle_model.calc_curvature(actuators.steerAngle*3.1415/180., CS.v_ego)

        # The use of the toggle below is handy for trying out the various LKAS modes
        if TOGGLE_DEBUG:
          self.lkas_action += int(CS.generic_toggle and not self.generic_toggle_last)
          self.lkas_action &= 0xf
        else:
          self.lkas_action = 5   # 4 and 5 seem the best. 8 and 9 seem to aggressive and laggy

        can_sends.append(create_steer_command(self.packer, apply_steer, enabled,
                                              CS.lkas_state, CS.angle_steers, curvature, self.lkas_action))
        self.generic_toggle_last = CS.generic_toggle

      if (frame % 100) == 0:

        can_sends.append(make_can_msg(973, b'\x00\x00\x00\x00\x00\x00\x00\x00', 0, False))
        #can_sends.append(make_can_msg(984, '\x00\x00\x00\x00\x80\x45\x60\x30', 0, False))

      if (frame % 100) == 0 or (self.enabled_last != enabled) or (self.main_on_last != CS.main_on) or \
         (self.steer_alert_last != steer_alert):
        can_sends.append(create_lkas_ui(self.packer, CS.main_on, enabled, steer_alert))

      if (frame % 200) == 0:
        can_sends.append(make_can_msg(1875, b'\x80\xb0\x55\x55\x78\x90\x00\x00', 1, False))

      if (frame % 10) == 0:

        can_sends.append(make_can_msg(1648, b'\x00\x00\x00\x40\x00\x00\x50\x00', 1, False))
        can_sends.append(make_can_msg(1649, b'\x10\x10\xf1\x70\x04\x00\x00\x00', 1, False))

        can_sends.append(make_can_msg(1664, b'\x00\x00\x03\xe8\x00\x01\xa9\xb2', 1, False))
        can_sends.append(make_can_msg(1674, b'\x08\x00\x00\xff\x0c\xfb\x6a\x08', 1, False))
        can_sends.append(make_can_msg(1675, b'\x00\x00\x3b\x60\x37\x00\x00\x00', 1, False))
        can_sends.append(make_can_msg(1690, b'\x70\x00\x00\x55\x86\x1c\xe0\x00', 1, False))

        can_sends.append(make_can_msg(1910, b'\x06\x4b\x06\x4b\x42\xd3\x11\x30', 1, False))
        can_sends.append(make_can_msg(1911, b'\x48\x53\x37\x54\x48\x53\x37\x54', 1, False))
        can_sends.append(make_can_msg(1912, b'\x31\x34\x47\x30\x38\x31\x43\x42', 1, False))
        can_sends.append(make_can_msg(1913, b'\x31\x34\x47\x30\x38\x32\x43\x42', 1, False))
        can_sends.append(make_can_msg(1969, b'\xf4\x40\x00\x00\x00\x00\x00\x00', 1, False))
        can_sends.append(make_can_msg(1971, b'\x0b\xc0\x00\x00\x00\x00\x00\x00', 1, False))

      static_msgs = range(1653, 1658)
      for addr in static_msgs:
        cnt = (frame % 10) + 1
        can_sends.append(make_can_msg(addr, (cnt<<4).to_bytes(1, 'little') + b'\x00\x00\x00\x00\x00\x00\x00', 1, False))

      self.enabled_last = enabled
      self.main_on_last = CS.main_on
      self.steer_alert_last = steer_alert

    return can_sends
