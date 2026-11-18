import os
import sys
import time
import traci

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

# SUMO hello tutorial config path
sumoConfig = r"C:\Program Files (x86)\SUMO\docs\tutorial\hello\data\hello.sumocfg"
sumoBinary = "sumo-gui"
traci.start([sumoBinary, "-c", sumoConfig])

step = 0
car_counter = 0

# Lamba loop chalayenge taaki jab tak aap chaho simulation chalti rahe
while step < 5000:
    traci.simulationStep()
    time.sleep(0.05)  # Screen par smooth movement ke liye delay

    # Har 15 steps ke baad ek nayi gaadi automatically road par bhej do
    if step % 15 == 0:
        veh_id = f"car_{car_counter}"
        try:
            # 'horiz' route par nayi gaadi add kar rahe hain
            traci.vehicle.add(vehID=veh_id, routeID="horiz", typeID="car")
            car_counter += 1
        except Exception as e:
            pass

    vehicle_ids = traci.vehicle.getIDList()
    print(f"Step {step}: Active vehicles = {len(vehicle_ids)}")

    step += 1

traci.close()
print("Simulation finished!")