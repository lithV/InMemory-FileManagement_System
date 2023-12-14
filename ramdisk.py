import os
import colorama
import shlex

class FileEntry:
    def __init__(self, name, is_directory=True, contents=None):
        self.name = name
        self.is_directory = is_directory
        if(is_directory):
            # If directory, then contents will be an
            # array of file entries
            self.contents = []
        else:
            self.contents = contents
    
    def __repr__(self):
        return f"Type: {'DIR' if self.is_directory else 'FILE'}\nName: {self.name}"

    def __str__(self):
        return f"Type: {'DIR' if self.is_directory else 'FILE'}\nName: {self.name}"
    
    def GetContents(self):
        return self.contents
    
class RAMDisk:
    def __init__(self):
        self.root = FileEntry('/')

    def CheckIfExists(self, directory, name):
        for entry in directory.contents:
            if(name == entry.name):
                return True
        return False
    
    def CheckIfDirExists(self, directory, name):
        for entry in directory.contents:
            if(name == entry.name and entry.is_directory == True):
                return True
        return False
    
    def TraversePath(self, path):
        current_directory = self.root
        paths = [p for p in path.split('/') if p != '']
        # Traverse tree
        for i in range(0, len(paths)):
            found = False
            for dir in current_directory.contents:
                if(dir.is_directory and dir.name == paths[i]):
                    current_directory = dir
                    found = True
                    break
            if(found == False):
                print("Error: Invalid Path given.")
                return None
        return current_directory
    
    def GetTraverseString(self, path):
        current_directory = self.root
        traverse_string = '/'
        paths = [p for p in path.split('/') if p != '']
        # Traverse tree
        for i in range(0, len(paths)):
            found = False
            for dir in current_directory.contents:
                if(dir.is_directory and dir.name == paths[i]):
                    current_directory = dir
                    found = True
                    traverse_string += f'{dir.name}/'
                    break
            if(found == False):
                print("Error: Invalid Path given.")
                return '/'
        return traverse_string
    
    def CreateDirectory(self, pathname):
        paths = [p for p in pathname.split('/') if p != '']
        dir_to_create = paths[-1]
        path_previous = '/'.join(paths[:-1])
        current_directory = self.TraversePath(path_previous)
        if(current_directory is None):
            return
        
        if(self.CheckIfExists(current_directory, dir_to_create)):
            print(f"Error: Cannot create {pathname}, path already exists.")
            return
        
        current_directory.contents.append(FileEntry(dir_to_create))
    
    def CreateFile(self, pathname, contents):
        paths = [p for p in pathname.split('/') if p != '']
        file_to_create = paths[-1]
        path_previous = '/'.join(paths[:-1])
        current_directory = self.TraversePath(path_previous)
        if(current_directory is None):
            return
        
        if(self.CheckIfExists(current_directory, file_to_create)):
            print(f"Error: Cannot create {pathname}, path already exists.")
            return
        
        current_directory.contents.append(FileEntry(file_to_create, False, contents))

    def RemoveEntry(self, pathname):
        paths = [p for p in pathname.split('/') if p != '']
        entry_to_remove = paths[-1]
        path_previous = '/'.join(paths[:-1])
        current_directory = self.TraversePath(path_previous)
        if(current_directory is None):
            return
        current_directory.contents = [entry for entry in current_directory.contents if entry.name != entry_to_remove]
    
    def CopyEntry(self, pathname_src, pathname_dest, remove=False):
        paths = [p for p in pathname_src.split('/') if p != '']
        entry_to_copy = paths[-1]
        path_previous = '/'.join(paths[:-1])
        source_directory = self.TraversePath(path_previous)

        paths = [p for p in pathname_dest.split('/') if p != '']
        entry_to_paste = paths[-1]
        path_previous = '/'.join(paths[:-1])
        destination_directory = self.TraversePath(path_previous)

        if(source_directory is None or destination_directory is None):
            print("Error: One of source or destination paths is invalid during this copy-paste operation.")
            return
        
        # Get source data
        src_file_entry = None
        for file in source_directory.contents:
            if(file.name == entry_to_copy):
                src_file_entry = file
                break

        if(src_file_entry == None):
            print("Entry to copy does not exist.")

        # Check if it is a directory or a file
        if(src_file_entry.is_directory):
            new_dir = FileEntry(entry_to_paste)
            new_dir.contents = src_file_entry.contents
            destination_directory.contents.append(new_dir)
        else:
            destination_directory.contents.append(FileEntry(entry_to_paste, False, src_file_entry.contents))
        
        if(remove):
            source_directory.contents = [entry for entry in source_directory.contents if entry.name != entry_to_copy]

    def ListDirectory(self, path):
        directory = self.TraversePath(path)
        if(directory.is_directory == False):
            print(f"{path} is not a directory.")
            return
        else:
            print(".    \t\tDIR\n..   \t\tDIR\n")
            for entry in directory.contents:
                if(entry.is_directory):
                    print(colorama.Fore.BLUE + f"{entry.name}/\t\tDIR\n" + colorama.Fore.RESET)
                else:
                    print(f"{entry.name}\tFILE\t{len(entry.contents)} BYTES\n")

class RAMDiskShell:
    def __init__(self, ramdisk):
        self.ramdisk = ramdisk
        self.current_directory = '/'
    
    def Shell(self):
        user_input = shlex.split(input(colorama.Fore.GREEN + "RAMDISK@" + colorama.Fore.BLUE + f"{self.current_directory}" + colorama.Fore.RESET + "$ "))
        command = user_input[0]

        # MKDIR - Create new directory
        if(command == 'mkdir'):
            if(len(user_input) != 2):
                print("USAGE: mkdir <Directory Name>")
                return
            else:
                self.ramdisk.CreateDirectory(self.current_directory + f'{user_input[1]}/')
        # TOUCH - Create new file
        elif(command == 'touch'):
            if(len(user_input) != 2):
                print("USAGE: touch <File Name>")
                return
            else:
                self.ramdisk.CreateFile(self.current_directory + f'{user_input[1]}', '')
        # CD - Change a directory
        elif(command == 'cd'):
            if(len(user_input) != 2):
                print("USAGE: cd <Directory Name>")
                return
            else:
                directory_to_change = user_input[1]
                # Check if directory to change is simply the previous directory
                if(directory_to_change == '..'):
                    self.current_directory = os.path.dirname(os.path.dirname(self.current_directory))
                    if(self.current_directory != '/'):
                        self.current_directory += '/'
                    return
                
                # Check if directory to change starts with '/', then we go with root.
                if(directory_to_change.startswith('/')):
                    dirptr = self.ramdisk.TraversePath(directory_to_change)
                    if(dirptr != None):
                        self.current_directory = self.ramdisk.GetTraverseString(directory_to_change)
                        return
                    else:
                        print("Error: No such path exists.")
                        return 
                    
                # Otherwise we have to look for in the working directory
                dirptr = self.ramdisk.TraversePath(self.current_directory + directory_to_change)
                if(dirptr != None):
                    self.current_directory = self.current_directory + f'{user_input[1]}/'
                else:
                    print("Error: No such directory exists.")
        # ECHO - Output to screen
        elif(command == 'echo'):
            if(len(user_input) == 2):
                print(user_input[1])
            elif(len(user_input) == 4):
                if(user_input[2] == '>'):
                    file_path = user_input[3]
                    directory = self.ramdisk.TraversePath(self.current_directory + os.path.dirname(file_path))
                    if(directory == None):
                        print("Error: No such path exists.")
                        return
                    for file in directory.contents:
                        if(file.name == os.path.basename(user_input[3]) and file.is_directory == False):
                            file.contents += user_input[1]
                            return
                    print('No such file exists.')
                    return
                else:
                    print("USAGE: echo 'text' > filename.txt")
            else:
                print("USAGE: echo 'text' > filename.txt")
        elif(command == 'ls'):
            self.ramdisk.ListDirectory(self.current_directory)
        # CAT - Show contents of a file
        elif(command == 'cat'):
            if(len(user_input) == 2):
                file_path = user_input[1]
                directory = self.ramdisk.TraversePath(self.current_directory + os.path.dirname(file_path))
                for file in directory.contents:
                    if(file.name == os.path.basename(file_path) and file.is_directory == False):
                        print(file.contents)
                        return
                    print('No such file exists.')
        # RM - Remove a directory
        elif(command == 'rm'):
            if(len(user_input) != 2):
                print('USAGE: rm <Directory or File Name>')
                return
            self.ramdisk.RemoveEntry(self.current_directory + f'{user_input[1]}')
        # CP - Copy a directory
        elif(command == 'cp' or command == 'mv'):
            if(len(user_input) != 3):
                print("USAGE: cp/mv <Source> <Destination>")
                return
            # First track the source and destination paths
            source_path = user_input[1]
            destination_path = user_input[2]
            
            if(source_path == '.'):
                source_path = self.current_directory
            elif(not source_path.startswith('/')):
                source_path = self.current_directory + source_path
            
            if(destination_path == '.'):
                destination_path = self.current_directory
            elif(not destination_path.startswith('/')):
                destination_path = self.current_directory + destination_path

            if(command == 'cp'):
                self.ramdisk.CopyEntry(source_path, destination_path)
            else:
                self.ramdisk.CopyEntry(source_path, destination_path, True)

        elif(command == 'exit'):
            exit(0)

rd = RAMDisk()
rs = RAMDiskShell(rd)

while True:
    rs.Shell()
