# 🚦 DynoPriority: Dynamic Traffic Control System with Emergency Override

An intelligent traffic signal control and simulation framework designed to optimize urban intersection flow dynamically while providing absolute real-time priority override for emergency vehicles (ambulances). Built using **SUMO (Simulation of Urban MObility)**, **TraCI (Traffic Control Interface)**, and a local **IoT HTTP server trigger**.

---

## 🚀 Key Features
* **Dynamic Congestion Control:** Continuously calculates real-time lane densities (`traci.edge.getLastStepVehicleNumber`) to adapt traffic light phases during normal traffic flow.
* **Distance-Based Ambulance Prioritization:** Scans approaching lanes and computes exact vehicle distances to the stop line, ensuring the ambulance closest to the intersection gets strict priority.
* **Multi-Directional Preemption:** Seamlessly handles emergency overrides across both North-South and East-West corridors.
* **IoT Hardware Simulation:** Integrated local HTTP server (`localhost:8080`) that listens for external hardware/RFID triggers to simulate remote emergency overrides.
* **Live Performance Analytics:** Tracks and logs cumulative Green and Red signal durations in real-time for performance evaluation.

---

## 🛠️ Tech Stack & Tools
* **Simulation Engine:** SUMO (Simulation of Urban MObility) & SUMO-GUI
* **Controller Interface:** Python (TraCI API, `threading`, `http.server`)
* **Environment:** Windows, IntelliJ IDEA, Git / Version Control

---

## 📂 Project Structure
```text
DynoPriority/
│
├── intersection/
│   ├── intersection.net.xml       # Network map definition
│   ├── intersection.rou.xml       # Route and vehicle definitions (including ambulances)
│   ├── intersection.sumocfg       # Main SUMO configuration file
│   ├── my_net.edg.xml             # Edge definitions
│   └── my_net.nod.xml             # Node definitions
│
├── traffic_controller.py          # Main Python controller (TraCI + IoT Server + Preemption Logic)
├── test_sumo.py                   # Simulation testing script
├── grid.net.xml                   # Alternative grid network layout
└── .gitignore                     # Git ignore rules for temporary IDE/venv files
