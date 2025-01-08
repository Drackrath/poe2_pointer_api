import ctypes
import ctypes.wintypes as wintypes
import psutil
from pymem import Pymem


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


def get_pointer(pm, base ,offsets):
    """
    Follows a series of pointers to get a value from memory.
    """
    addr = pm.read_longlong(base) 
    for i in offsets:
        if i != offsets[-1]:
            addr = pm.read_longlong(addr + i)
    return pm.read_int(addr + offsets[-1]) 
