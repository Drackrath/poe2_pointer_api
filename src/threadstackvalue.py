import ctypes
import psutil
import sys
from ctypes import wintypes

# Constants
THREAD_QUERY_INFORMATION = 0x40
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

# Define Windows API function prototypes
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

# Structure for Process Information
class THREADENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ThreadID", wintypes.DWORD),
                ("th32OwnerProcessID", wintypes.DWORD),
                ("tpBasePri", wintypes.LONG),
                ("tpDeltaPri", wintypes.LONG),
                ("dwFlags", wintypes.DWORD)]

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", wintypes.ULONG),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_char * 260)]


def get_process_handle(pid):
    return kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)


def list_threads(pid):
    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000004, pid)  # TH32CS_SNAPTHREAD
    thread_entry = THREADENTRY32()
    thread_entry.dwSize = ctypes.sizeof(THREADENTRY32)
    
    if kernel32.Thread32First(snapshot, ctypes.byref(thread_entry)):
        while True:
            if thread_entry.th32OwnerProcessID == pid:
                yield thread_entry
            if not kernel32.Thread32Next(snapshot, ctypes.byref(thread_entry)):
                break


def read_memory(handle, address, size):
    buffer = ctypes.create_string_buffer(size)
    bytes_read = wintypes.DWORD(0)
    if kernel32.ReadProcessMemory(handle, address, buffer, size, ctypes.byref(bytes_read)):
        return buffer.raw
    else:
        return None


def get_thread_stack_address(thread_id):
    # Assuming you have some way of identifying the stack of interest.
    # You can use THREAD_QUERY_INFORMATION or inspect the stack manually.
    pass


def main():
    # Find the process (Path of Exile Steam)
    process_name = "PathOfExileSteam.exe"
    pid = None

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            break

    if pid is None:
        print(f"Process {process_name} not found.")
        sys.exit(1)

    print(f"Found process {process_name} with PID {pid}")

    # Get a handle to the process
    process_handle = get_process_handle(pid)
    
    if not process_handle:
        print(f"Unable to open process {process_name} with PID {pid}")
        sys.exit(1)

    # Now, we will list threads and inspect memory addresses.
    for thread in list_threads(pid):
        print(f"Thread ID: {thread.th32ThreadID}, Owner Process ID: {thread.th32OwnerProcessID}")

        # If you know the thread stack, you could now analyze its contents.
        # For example, find and read the stack pointer (to get the address).
        # Here you would need to read the thread's memory region.
        stack_address = get_thread_stack_address(thread.th32ThreadID)
        if stack_address:
            stack_data = read_memory(process_handle, stack_address, 128)  # Read 128 bytes
            if stack_data:
                print(f"Stack data: {stack_data.hex()}")
            else:
                print("Failed to read memory.")
        else:
            print("No valid stack address found.")

    # Close the handle to the process when done.
    kernel32.CloseHandle(process_handle)


if __name__ == "__main__":
    main()
