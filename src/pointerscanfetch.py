from pymem import Pymem
import pointerservice as ps

process_name = "PathOfExileSteam.exe"
pid = ps.get_pid(process_name) 

# Get the base address of the module
pm = Pymem(process_name)
allocationbase_address = ps.get_module_base_address(process_name)

# Base offsets for each value
base_offset_gold = 0x03891F00 
base_offset_current_life = 0x03B8C1B0
base_offset_guild_exalted = 0x03891E90
base_offset_dex = 0x03B8DF28

base_address_gold = allocationbase_address + base_offset_gold
base_address_current_life = allocationbase_address + base_offset_current_life
base_address_guild_exalted = allocationbase_address + base_offset_guild_exalted
base_address_dex = allocationbase_address + base_offset_dex

# Offsets to follow
offsetmap = {
"gold" : [0xA8, 0x8, 0xC78, 0x48, 0x8, 0x1E8, 0x2A48],
"current_life" : [0x148, 0x88, 0x48, 0x10, 0x20, 0x68, 0x464],
"guild_exalted" : [0x70, 0x258, 0x8, 0x120, 0x8, 0xA0, 0xB8, 0x30, 0x0 ,0x10, 0x10, 0x18],
"dex" : [0x38, 0xA8, 0x30, 0x48, 0x10, 0x238, 0x1F8]
}


goldvalue = ps.get_pointer(pm, base_address_gold, offsetmap["gold"])
current_life = ps.get_pointer(pm, base_address_current_life, offsetmap["current_life"])
dex = ps.get_pointer(pm, base_address_dex, offsetmap["dex"])


print(f"Gold Value: {goldvalue}")
print(f"Current Life: {current_life}")
print(f"Dex: {dex}")

# No use, since its only updating the value when the player opens the guild stash
# Too volatile pointers to be useful
try:
    guild_exalted = ps.get_pointer(pm, base_address_guild_exalted, offsetmap["guild_exalted"])
    print(f"Guild Exalted: {guild_exalted}")
except:
    print("Guild Exalted: Not available")




# Possible values?
# "current_life" : [0x148, 0x88, 0x48, 0x10, 0x20, 0x68, 0x464]
# current_life = ps.get_pointer(base_address, offsetmap["current_life"])
# print(f"Current Life: {current_life}")
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