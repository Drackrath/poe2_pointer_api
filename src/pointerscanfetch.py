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

print(f"allocationbase_address_threadstack0: {hex(allocationbase_address_threadstack0)}")

ct_file_path = r'C:\Development Tools\VSCodeProjects\POE2DPSVALUEChecker\cheatengine\Path of Exile 2 current_life.ct'
pointer_entry = ps.get_pointer_from_ct_file(ct_file_path, "current_life_patch_e+f")
print(f"pointer_entry: {pointer_entry}")

base_offset_currentlife = pointer_entry["BaseOffset"]

print(f"base_offset_currentlife: {hex(base_offset_currentlife)}")

base_address = allocationbase_address_threadstack0 + base_offset_currentlife
print (f"base_address: {hex(base_address)}")

# Offsets to follow
offsetmap = {
    "current_health": pointer_entry["Offsets"],
}

value = ps.get_pointer(pm, base_address, offsetmap["current_health"])

print(f"current_health: {value}")