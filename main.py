import subprocess
import os
import time

def run_whisper_command():
    # Define the output directory and file name
    output_dir = './output'
    output_file = os.path.join(output_dir, 'transcription.txt')

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define the command and arguments
    command = ['./stream', '-m', './models/ggml-base.en.bin', '-t', '8', '--step', '500', '--length', '10000']

    # Execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    # Open a file to write the output
    with open(output_file, 'w') as output_file:
        current_segment = []
        silence_start_time = None

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())  # Print to console for real-time feedback

                # Append the output to the current segment
                current_segment.append(output.strip())

                # Check for the "STOP LISTENING" command
                if "Stop listening" in output:
                    print("STOP LISTENING command detected. Terminating the program.")
                    current_segment = []
                    break

                # Check for silence
                if '[BLANK_AUDIO]' in output or '[inaudible]' in output:
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time > 2:  # 2 seconds of silence
                        # Write the completed segment to the file
                        if current_segment:
                            if "Stop listening" not in ' '.join(current_segment):
                                print(f"Writing segment to file: {current_segment}")  # Debug info
                                output_file.write('\n'.join(current_segment) + '\n')
                                output_file.flush()  # Ensure data is written to disk
                            current_segment = []
                        silence_start_time = None
                else:
                    silence_start_time = None

        # Write any remaining output after the process completes, if STOP LISTENING was not detected
        if current_segment and "Stop listening" not in ' '.join(current_segment):
            print(f"Writing remaining segment to file: {current_segment}")  # Debug info
            output_file.write('\n'.join(current_segment) + '\n')
            output_file.flush()  # Ensure data is written to disk

    # Capture any errors
    stderr_output = process.stderr.read()
    if stderr_output:
        print("Errors occurred:")
        print(stderr_output)
    else:
        print("Transcription completed successfully.")

if __name__ == "__main__":
    run_whisper_command()
