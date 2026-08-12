@service
@state_trigger("binary_sensor.tibber_pool_schedule")
def pool_pump_controller(value=None, old_value=None):
    PUMP_ENTITY = "switch.osram_plug_01_switch_6"
    current_state = switch.osram_plug_01_switch_6
    
    if value == "on":
        if current_state != "on":
            log.info("Tibber Pool Schedule ist ON. Schalte Pumpe ein.")
            switch.turn_on(entity_id=PUMP_ENTITY)
    else:
        if current_state != "off":
            log.info("Tibber Pool Schedule ist OFF. Schalte Pumpe aus.")
            switch.turn_off(entity_id=PUMP_ENTITY)

@service
@time_trigger("startup")
def init_pool_pump():
    log.info("Pool Pump Controller started.")
