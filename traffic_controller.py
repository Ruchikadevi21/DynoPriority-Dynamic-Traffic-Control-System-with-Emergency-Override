import traci
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

external_iot_trigger = False

class IoTHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        global external_iot_trigger
        if self.path == '/ambulance_detected':
            external_iot_trigger = True
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"IoT Alert Received!")
            print("\n>>> [IoT HARDWARE TRIGGERED] Emergency override activated! <<<")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server():
    server = ('localhost', 8080)
    httpd = HTTPServer(server, IoTHandler)
    httpd.serve_forever()

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# --- SUMO Startup ---
sumoBinary = "sumo-gui"
sumoConfig = "intersection/intersection.sumocfg"
traci.start([sumoBinary, "-c", sumoConfig])

tls_id = "C"
step = 0
preemption_hold_counter = 0

# Duration counters in seconds
ns_green_time = 0
ns_red_time = 0
ew_green_time = 0
ew_red_time = 0

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    emergency_detected = False
    target_phase = None
    detected_direction = ""
    closest_distance = float('inf')

    vehicle_ids = traci.vehicle.getIDList()

    # SCAN ALL VEHICLES TO FIND THE AMBULANCE CLOSEST TO THE STOP LINE
    for veh_id in vehicle_ids:
        v_type = traci.vehicle.getTypeID(veh_id).lower()
        current_edge = traci.vehicle.getRoadID(veh_id)

        if "ambulance" in v_type or "amb" in veh_id.lower():
            if current_edge in ["N-C", "S-C", "E-C", "W-C"]:
                try:
                    lane_id = traci.vehicle.getLaneID(veh_id)
                    lane_length = traci.lane.getLength(lane_id)
                    veh_position = traci.vehicle.getLanePosition(veh_id)
                    distance_to_light = lane_length - veh_position

                    if distance_to_light < closest_distance:
                        closest_distance = distance_to_light
                        emergency_detected = True

                        if current_edge in ["N-C", "S-C"]:
                            target_phase = 0  # North-South Green
                            detected_direction = f"North-South ({current_edge})"
                        else:
                            target_phase = 2  # East-West Green
                            detected_direction = f"East-West ({current_edge})"
                except Exception:
                    pass

    # 1. EMERGENCY PREEMPTION: Trigger only when the ambulance is close to the stop line (< 35 meters)
    # This allows it to briefly arrive and wait so you can visually confirm the red light before priority kicks in.
    if (emergency_detected and closest_distance < 35) or external_iot_trigger:
        if external_iot_trigger and target_phase is None:
            target_phase = 0
            detected_direction = "API Triggered"

        traci.trafficlight.setPhase(tls_id, target_phase)

        if step % 10 == 0:
            print(f"[Step {step}] 🚨 AMBULANCE WAITING AT LIGHT ({closest_distance:.1f}m away) -> FORCING GREEN for {detected_direction}!")

    else:
        # 2. DYNAMIC CONGESTION-BASED CONTROL
        ns_congestion = traci.edge.getLastStepVehicleNumber("N-C") + traci.edge.getLastStepVehicleNumber("S-C")
        ew_congestion = traci.edge.getLastStepVehicleNumber("E-C") + traci.edge.getLastStepVehicleNumber("W-C")

        if ns_congestion >= ew_congestion:
            target_phase = 0  # N-S Green
        else:
            target_phase = 2  # E-W Green

        traci.trafficlight.setPhase(tls_id, target_phase)

    # Track metrics
    active_phase = traci.trafficlight.getPhase(tls_id)
    if active_phase == 0:
        ns_green_time += 1
        ew_red_time += 1
    elif active_phase == 2:
        ew_green_time += 1
        ns_red_time += 1

    # Print status every 20 steps
    if step % 20 == 0:
        print(f"[Step {step}] Phase Active: {active_phase} | N-S [G: {ns_green_time}s] | E-W [G: {ew_green_time}s]")

    step += 1
    time.sleep(0.05)

traci.close()