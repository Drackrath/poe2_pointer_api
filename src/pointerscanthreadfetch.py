# Based on the patch from 0.1.0e to 0.1.0f all Pointer values have changed.
# The offset calculation is similar in a Threadstack of the game.
# Therefore the pointers can be calculated from 2 different patches with the application of Pymem being THREADSTACK0.
# New Pointers should also be found within the THREADSTACK0 application to ensure patch proofing.


import ctypes
from ctypes import wintypes
from pymem import Pymem

# Constants
TH32CS_SNAPTHREAD = 0x00000004
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04

# Define MEMORY_BASIC_INFORMATION structure
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]

# Define THREADENTRY32 structure
class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ThreadID", wintypes.DWORD),
        ("th32OwnerProcessID", wintypes.DWORD),
        ("tpBasePri", wintypes.LONG),
        ("tpDeltaPri", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
    ]

# Function to enumerate memory regions
def enumerate_memory_regions(process_handle):
    VirtualQueryEx = ctypes.windll.kernel32.VirtualQueryEx
    VirtualQueryEx.argtypes = [
        wintypes.HANDLE,  # hProcess
        wintypes.LPCVOID,  # lpAddress
        ctypes.POINTER(MEMORY_BASIC_INFORMATION),  # lpBuffer
        ctypes.c_size_t,  # dwLength
    ]
    VirtualQueryEx.restype = ctypes.c_size_t

    mbi = MEMORY_BASIC_INFORMATION()
    address = 0  # Start address

    regions = []
    while address < 0x7FFFFFFF:  # Max user space memory
        result = VirtualQueryEx(process_handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi))
        if result == 0:
            break
        if mbi.State == MEM_COMMIT and mbi.Protect == PAGE_READWRITE:
            regions.append((mbi.BaseAddress, mbi.RegionSize))
        address += mbi.RegionSize
    return regions

# Function to enumerate threads in the process
def enumerate_threads(process_id):
    CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    Thread32First = ctypes.windll.kernel32.Thread32First
    Thread32Next = ctypes.windll.kernel32.Thread32Next

    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    thread_entry = THREADENTRY32()
    thread_entry.dwSize = ctypes.sizeof(THREADENTRY32)

    threads = []
    if Thread32First(snapshot, ctypes.byref(thread_entry)):
        while True:
            if thread_entry.th32OwnerProcessID == process_id:
                threads.append(thread_entry.th32ThreadID)
            if not Thread32Next(snapshot, ctypes.byref(thread_entry)):
                break
    return threads

def find_threadstack0_base_address(process_handle, thread_id):
    # Define THREAD_BASIC_INFORMATION structure
    class THREAD_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("ExitStatus", wintypes.LONG),
            ("TebBaseAddress", ctypes.c_void_p),
            ("ClientId", ctypes.c_ulong * 2),
            ("AffinityMask", ctypes.POINTER(ctypes.c_ulong)),
            ("Priority", wintypes.LONG),
            ("BasePriority", wintypes.LONG),
        ]

    # Get thread information
    NtQueryInformationThread = ctypes.windll.ntdll.NtQueryInformationThread
    NtQueryInformationThread.argtypes = [
        wintypes.HANDLE,  # ThreadHandle
        wintypes.ULONG,  # ThreadInformationClass
        ctypes.POINTER(THREAD_BASIC_INFORMATION),  # ThreadInformation
        wintypes.ULONG,  # ThreadInformationLength
        ctypes.POINTER(wintypes.ULONG),  # ReturnLength
    ]
    NtQueryInformationThread.restype = wintypes.LONG

    thread_handle = ctypes.windll.kernel32.OpenThread(0x001F03FF, False, thread_id)
    if not thread_handle:
        error_code = ctypes.windll.kernel32.GetLastError()
        raise Exception(f"Failed to open thread {thread_id}. Error code: {error_code}")

    tbi = THREAD_BASIC_INFORMATION()
    result = NtQueryInformationThread(thread_handle, 0, ctypes.byref(tbi), ctypes.sizeof(tbi), None)
    ctypes.windll.kernel32.CloseHandle(thread_handle)

    if result != 0:
        error_code = ctypes.windll.kernel32.GetLastError()
        raise Exception(f"Failed to query thread information for thread {thread_id}. Error code: {result}, System error code: {error_code}")

    return tbi.TebBaseAddress

# Main logic
def find_threadstack0(process_name):
    pm = Pymem(process_name)
    process_handle = pm.process_handle
    process_id = pm.process_id

    # Enumerate threads
    threads = enumerate_threads(process_id)
    print(f"Threads for process {process_name} (PID: {process_id}): {threads}")

    # Enumerate memory regions
    memory_regions = enumerate_memory_regions(process_handle)
    print(f"Memory regions: {len(memory_regions)} regions found")

if __name__ == "__main__":
    target_process = "PathOfExileSteam.exe"  # Replace with your target process
    find_threadstack0(target_process)

    # Get the base address value of the first thread of the process
    pm = Pymem(target_process)
    process_handle = pm.process_handle
    process_id = pm.process_id

    threads = enumerate_threads(process_id)
    if threads:
        first_thread_id = threads[0]
        base_address = find_threadstack0_base_address(process_handle, first_thread_id)
        print(f"Base address of the first thread (ID: {first_thread_id}): {base_address}")
    else:
        print("No threads found for the process.")
