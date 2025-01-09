# Based on the patch from 0.1.0e to 0.1.0f all Pointer values have changed.
# The offset calculation is similar in a Threadstack of the game.
# Therefore the pointers can be calculated from 2 different patches with the application of Pymem being THREADSTACK0.
# New Pointers should also be found within the THREADSTACK0 application to ensure patch proofing.
# using c++ tool threadstack.exe to find the base address of the threadstack0

from pymem import Pymem
import pointerservice as ps

process_name = "PathOfExileSteam.exe"
pid = ps.get_pid(process_name) 

print(f"PID: {pid}")
# Get the base address of the module
pm = Pymem(process_name)
allocationbase_address = ps.get_module_base_address(process_name)
allocationbase_address_threadstack0 = ps.get_threadstack0_base_address(pid)

print(f"allocationbase_address_threadstack0: {allocationbase_address_threadstack0}")

base_offset_currentlife = -0x000001C8

base_address = allocationbase_address_threadstack0 + base_offset_currentlife             

# Offsets to follow
offsetmap = {
"current_health" : [0x38, 0x8, 0x110, 0x30, 0x48, 0x10, 0x20, 0x60, 0xA0, 0x48, 0x18, 0x378],
}
value = ps.get_pointer(pm, base_address, offsetmap["current_health"])

print(f"current_health: {value}")