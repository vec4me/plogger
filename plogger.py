import os
import sublime
import sublime_plugin
import subprocess
import time


class SavePLGFileCommand(sublime_plugin.EventListener):

    def on_post_save_async(self, view):
        # Get the file path of the saved PLG file
        file_path = view.file_name()

        # Ensure the file is a PLG file
        if file_path.endswith(".plg"):
            # Generate the checksum using md5sum command
            checksum = self.generate_checksum(file_path)

            # Get the path of the state file in the same folder as the PLG file
            state_file_path = self.get_state_file_path(file_path)

            # Read the latest entry from the state file (if present)
            latest_entry = self.get_latest_entry(state_file_path, checksum)

            # Check if the current checksum matches the latest entry
            if latest_entry:
                print(checksum, latest_entry[0])
                if checksum != latest_entry[0]:
                    # Append the new entry to the state file
                    self.append_entry(state_file_path, checksum, "a")
            else:
                self.append_entry(state_file_path, checksum, "w")

    def generate_checksum(self, file_path):
        # Run the md5sum command on the PLG file
        result = subprocess.run(["md5sum", file_path],
                                capture_output=True,
                                text=True)

        # Extract the checksum from the command output
        checksum = result.stdout.split()[0]

        return checksum

    def get_state_file_path(self, plg_file_path):
        # Get the folder path of the PLG file
        folder_path = os.path.dirname(plg_file_path)

        # Construct the state file path using the PLG file's folder path
        state_file_path = os.path.join(folder_path, "state.txt")

        return state_file_path

    def get_latest_entry(self, state_file_path, checksum):
        try:
            # Read the state file
            with open(state_file_path, "r") as state_file:
                # Get the last line in the file
                lines = state_file.readlines()
                if lines:
                    latest_entry = lines[-1].split()
                    print(latest_entry, "ASD")
                    return latest_entry
        except FileNotFoundError:
            return [None, None]

    def append_entry(self, state_file_path, checksum, typee):
        # Get the current UNIX timestamp
        timestamp = int(time.time())

        # Append the new entry to the state file
        with open(state_file_path, typee) as state_file:
            state_file.write(f"{checksum} {timestamp}\n")