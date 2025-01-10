# Based on the patch from 0.1.0e to 0.1.0f all Pointer values have changed.
# The offset calculation is similar in a Threadstack of the game.
# Therefore the pointers can be calculated from 2 different patches with the application of Pymem being THREADSTACK0.
# New Pointers should also be found within the THREADSTACK0 application to ensure patch proofing.
# using c++ tool threadstack.exe to find the base address of the threadstack0

from pymem import Pymem
import src.pointerservice as ps

process_name = "PathOfExileSteam.exe"
pid = ps.get_pid(process_name) 

print(f"PID: {pid}")
# Get the base address of the module
pm = Pymem(process_name)
allocationbase_address = ps.get_module_base_address(process_name)
allocationbase_address_threadstack0 = ps.get_threadstack0_base_address(pid)

print(f"allocationbase_address_threadstack0: {hex(allocationbase_address_threadstack0)}")

ct_file_path_current_life = r'C:\Development Tools\VSCodeProjects\POE2DPSVALUEChecker\cheatengine\Path of Exile 2 current_life.ct'
ct_file_path_current_mana = r'C:\Development Tools\VSCodeProjects\POE2DPSVALUEChecker\cheatengine\Path of Exile 2 current_mana.ct'
pointer_entry_current_life = ps.get_pointer_from_ct_file(ct_file_path_current_life, "current_life_patch_e+f")
pointer_entry_current_mana = ps.get_pointer_from_ct_file(ct_file_path_current_mana, "current_mana_0.1.0f")

print(f"pointer current_life: {pointer_entry_current_life}")
print(f"pointer current_mana: {pointer_entry_current_mana}")

base_offset_current_life = pointer_entry_current_life["BaseOffset"]
base_offset_current_mana = pointer_entry_current_mana["BaseOffset"]

print(f"base_offset_current_life: {hex(base_offset_current_life)}")
print(f"base_offset_current_mana: {hex(base_offset_current_mana)}")


# Patch Values // Need rescan after Patch
base_address_current_mana = allocationbase_address + base_offset_current_mana
# Threadstack values
base_address_current_life = allocationbase_address_threadstack0 + base_offset_current_life

print (f"base_address_current_life: {hex(base_address_current_life)}")
print (f"base_address_current_mana: {hex(base_address_current_mana)}")

# Offsets to follow
offsetmap = {
    "current_health": pointer_entry_current_life["Offsets"],
    "current_mana": pointer_entry_current_mana["Offsets"]
}

current_life = ps.get_pointer(pm, base_address_current_life, offsetmap["current_health"])
current_mana = ps.get_pointer(pm, base_address_current_mana, offsetmap["current_mana"])

print(f"current_health: {current_life}")
print(f"current_mana: {current_mana}")
