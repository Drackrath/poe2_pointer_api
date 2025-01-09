import ctypes
import ctypes.wintypes as wintypes
import psutil
from pymem import Pymem
import subprocess
import xml.etree.ElementTree as ET

def get_pid(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None

def get_module_base_address(process_name):
    # Get all running processes
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            break
    else:
        raise Exception(f"Process '{process_name}' not found")

    # Open the process with necessary permissions
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    process_handle = ctypes.windll.kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid
    )
    if not process_handle:
        raise Exception("Failed to open process")

    # Get the base address of the module
    class MODULEINFO(ctypes.Structure):
        _fields_ = [
            ("lpBaseOfDll", wintypes.LPVOID),
            ("SizeOfImage", wintypes.DWORD),
            ("EntryPoint", wintypes.LPVOID),
        ]

    module_info = MODULEINFO()
    h_module = ctypes.c_void_p()
    h_modules = (ctypes.c_void_p * 1024)()
    needed = wintypes.DWORD()

    if ctypes.windll.psapi.EnumProcessModules(process_handle, ctypes.byref(h_modules), ctypes.sizeof(h_modules), ctypes.byref(needed)):
        h_module = ctypes.c_void_p(h_modules[0])  # Cast to ctypes.c_void_p
        ctypes.windll.psapi.GetModuleInformation(process_handle, h_module, ctypes.byref(module_info), ctypes.sizeof(module_info))
    else:
        raise Exception("Failed to enumerate process modules")

    # Close the process handle
    ctypes.windll.kernel32.CloseHandle(process_handle)

    return module_info.lpBaseOfDll

def get_threadstack0_base_address(pid):
    """
    Executes threadstack.exe with the given PID and returns the BASE ADDRESS of THREADSTACK 0.
    """
    result = subprocess.run([r'C:\Development Tools\VSCodeProjects\POE2DPSVALUEChecker\src\threadstack.exe', str(pid)], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Failed to execute threadstack.exe")

    for line in result.stdout.splitlines():
        if "THREADSTACK 0 BASE ADDRESS" in line:
            return int(line.split(':')[-1].strip(), 16)

    raise Exception("THREADSTACK 0 BASE ADDRESS not found in output")

def get_pointer(pm, base ,offsets):
    """
    Follows a series of pointers to get a value from memory.
    """
    addr = pm.read_longlong(base) 
    for i in offsets:
        if i != offsets[-1]:
            addr = pm.read_longlong(addr + i)
    return pm.read_int(addr + offsets[-1])

def get_pointer_from_ct_file(ct_file_path, variable_name):
    """
    Reads the specified Cheat Engine .ct file and returns the pointer cheat entry for the given variable.
    """
    tree = ET.parse(ct_file_path)
    root = tree.getroot()

    for cheat_entry in root.findall(".//CheatEntry"):
        description = cheat_entry.find("Description")
        if description is not None and variable_name in description.text:
            # Find the nested CheatEntry for the pointer scan result
            nested_entry = cheat_entry.find(".//CheatEntry")
            if nested_entry is not None:
                address = nested_entry.find("Address").text
                if '-' in address:
                    base_offset = -int(address.split('-')[-1], 16)
                elif '+' in address:
                    base_offset = int(address.split('+')[-1], 16)
                else:
                    base_offset = 0
                offsets = [int(offset.text, 16) for offset in nested_entry.find("Offsets").findall("Offset")]
                offsets.reverse()  # Reverse the order of offsets to read them bottom-up
                pointer_entry = {
                    "ID": nested_entry.find("ID").text,
                    "Description": nested_entry.find("Description").text,
                    "Address": address,
                    "BaseOffset": base_offset,
                    "Offsets": offsets
                }
                return pointer_entry

    raise Exception(f"Pointer cheat entry for variable '{variable_name}' not found in .ct file")

def get_nth_group_entry_value(ct_file_path, group_description, n):
    """
    Reads the specified Cheat Engine .ct file and returns the value for the n-th entry in the group entry.
    """
    tree = ET.parse(ct_file_path)
    root = tree.getroot()

    for group_entry in root.findall(".//CheatEntry"):
        description = group_entry.find("Description")
        if description is not None and group_description in description.text:
            group_entries = group_entry.findall(".//CheatEntry")
            if len(group_entries) > n:
                return group_entries[n]
            else:
                raise Exception(f"Group entry '{group_description}' does not have {n} entries")

    raise Exception(f"Group entry '{group_description}' not found in .ct file")
