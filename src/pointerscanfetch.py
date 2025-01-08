from pymem import Pymem
import pointerservice as ps

# Example Usage
process_name = "PathOfExileSteam.exe"
pid = ps.get_pid(process_name) 

# Get the base address of the module
pm = Pymem(process_name)
allocationbase_address = ps.get_module_base_address(process_name)
base_offset = 0x03891F00 
base_address = allocationbase_address + base_offset

# Offsets to follow
offsetmap = {
"gold" : [0xA8, 0x8, 0xC78, 0x48, 0x8, 0x1E8, 0x2A48]
}

goldvalue = ps.get_pointer(base_address, offsetmap["gold"])

print(f"Gold Value: {goldvalue}")




# Possible values?

# "energy shield" : 
# "life" :
# "mana" :
# "exp" :
# "str" :
# "dex" :
# "int" :
# "attack speed" :
# "cast speed" :
# "critical strike chance" :
# "critical strike multiplier" :
# "fire resistance" :
# "cold resistance" :
# "lightning resistance" :
# "chaos resistance" :
# "elemental resistance" :