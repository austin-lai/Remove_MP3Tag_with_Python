import os
import signal  # Import signal to handle Ctrl+C interruptions
import json  # Import json to save results in JSON format
from mutagen.id3 import ID3, ID3NoHeaderError, TXXX, COMM  # Import necessary classes for ID3 tags
from mutagen.apev2 import APEv2, APENoHeaderError  # Import necessary classes for APEv2 tags
from mutagen.mp3 import MP3  # Import class for MP3 files
from mutagen.mp4 import MP4  # Import class for MP4 files
from colorama import init, Fore, Back  # Import colorama for colored terminal output

# Initialize colorama to automatically reset colors after each print
init(autoreset=True)

# Add this global variable at the top of your script
all_results = []  # Global variable to store results

# Function to handle script termination when Ctrl+C is pressed and save results before exiting
def signal_handler(sig, frame):
    print(f"\n")  # Print a new line for better readability
    print(f"{Back.RED}{Fore.WHITE}Script terminated by user (Ctrl+C).")  # Notify the user of termination
    # Save results if any exist
    if all_results:
        save_results("", all_results)  # Save the results before exiting
    exit(0)  # Exit the script

# Register the signal handler for Ctrl+C interruptions
signal.signal(signal.SIGINT, signal_handler)

# Function to read ID3 tags from MP3 files
def read_id3_tags(file_path):
    try:
        audio = MP3(file_path)  # Create an MP3 object for the specified file
        tags = audio.tags  # Retrieve the tags from the audio file
        if tags is None:
            raise ID3NoHeaderError  # Raise an error if no tags are found
        print(f"{Back.BLACK}{Fore.WHITE}Successfully read ID3 tags from {file_path}")  # Notify success
        return tags  # Return the tags
    except ID3NoHeaderError:
        print(f"{Back.BLACK}{Fore.WHITE}No ID3 tags found in {file_path}")  # Notify no tags found
        return None  # Return None if no tags found
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error reading ID3 tags from {file_path}: {e}")  # Notify any other errors
        return None  # Return None on error

# Function to read APE tags from audio files
def read_ape_tags(file_path):
    try:
        tags = APEv2(file_path)  # Create an APEv2 object for the specified file
        print(f"{Back.BLACK}{Fore.WHITE}Successfully read APE tags from {file_path}")  # Notify success
        return tags  # Return the tags
    except APENoHeaderError:
        print(f"{Back.BLACK}{Fore.WHITE}No APE tags found in {file_path}")  # Notify no tags found
        return None  # Return None if no tags found
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error reading APE tags from {file_path}: {e}")  # Notify any other errors
        return None  # Return None on error

# Function to read MP4 tags from .m4a files
def read_mp4_tags(file_path):
    try:
        audio = MP4(file_path)  # Create an MP4 object for the specified file
        tags = audio.tags  # Retrieve the tags from the audio file
        if tags is None:
            print(f"{Back.BLACK}{Fore.WHITE}No MP4 tags found in {file_path}")  # Notify no tags found
            return None  # Return None if no tags found
        print(f"{Back.BLACK}{Fore.WHITE}Successfully read MP4 tags from {file_path}")  # Notify success
        return tags  # Return the tags
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error reading MP4 tags from {file_path}: {e}")  # Notify any other errors
        return None  # Return None on error

# Function to search for keywords in the provided tags
def search_keywords(tags, keywords, not_keywords):
    results = []  # Initialize a list to store found results
    for key, value in tags.items():  # Iterate through each tag

        # Debug key
        # print(f"Key: {key}, Type: {type(key)}")
        
        # Skip "cover art" and "acoustid fingerprint" field
        if "cover art" in str(key).lower() or "acoustid fingerprint" in str(key).lower() or "covr" in str(key).lower():
            continue  # Skip the iteration if the key contains "cover art" and "acoustid fingerprint"
        
        # Check for extended fields like TXXX and COMM
        elif isinstance(value, (TXXX, COMM)) or isinstance(tags, APEv2):
            for keyword in keywords:  # Iterate through each keyword
                # Check if keyword is present and not in not_keywords
                if keyword.lower() in str(value).lower() and not any(nk.lower() in str(value).lower() for nk in not_keywords):
                    results.append((key, value))  # Append the found key and value to results
                    print(f"{Back.BLACK}{Fore.GREEN}Keyword '{keyword}' found in field '{key}' with value '{value}' (excluding not_keywords)")
        elif isinstance(value, (list, str)): # Check for extended fields like TXXX and COMM in MP4

            value_str = str(value[0]).encode('utf-8', errors='replace').decode('utf-8') if isinstance(value, list) else str(value).encode('utf-8', errors='replace').decode('utf-8')
            
            for keyword in keywords:
                if keyword.lower() in value_str.lower() and not any(nk.lower() in value_str.lower() for nk in not_keywords):
                    results.append((key, value))
                    print(f"{Back.BLACK}{Fore.GREEN}Keyword '{keyword}' found in field '{key}' with value '{value}' (excluding not_keywords)")

    # Handle extended fields for MP4
    if isinstance(tags, MP4):
        for key, value in tags.items():  # Iterate through each tag in MP4
            value_str = str(value)  # Convert value to string
            for keyword in keywords:  # Iterate through each keyword
                # Check if keyword is present and not in not_keywords
                if keyword.lower() in value_str.lower() and not any(nk.lower() in value_str.lower() for nk in not_keywords):
                    results.append((key, value))  # Append the found key and value to results
                    print(f"{Back.BLACK}{Fore.GREEN}Keyword '{keyword}' found in extended field '{key}' with value '{value}' (excluding not_keywords)")

    return results  # Return the list of results found

# Function to save results to a JSON file with versioning
def save_results(file_path, results):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")  # Get the user's desktop path, this will work on both Windows and Unix-based systems
    
    # Create a versioned filename
    base_filename = 'id3_search_results'  # Base filename for the results
    version = 1  # Start versioning from 1
    result_file = os.path.join(desktop, f"{base_filename}_v{version}.json")  # Create the initial filename

    # Increment version number if the file already exists
    while os.path.exists(result_file):
        version += 1  # Increment version number
        result_file = os.path.join(desktop, f"{base_filename}_v{version}.json")  # Update the filename
    
    # Only create the file if there are results
    if results:
        # Prepare results for JSON serialization
        json_results = []
        for file_path, res in results:  # Iterate through each result
            entry = {"file": file_path, "tags": []}  # Create a dictionary for the current file
            for key, value in res:  # Iterate through each result in the current file
                entry["tags"].append({key: str(value)})  # Append the key-value pair to the tags list
            json_results.append(entry)  # Append the entry to json_results

        with open(result_file, 'w', encoding='utf-8', errors='replace') as f:  # Open the file for writing with UTF-8 encoding
            json.dump(json_results, f, ensure_ascii=False, indent=4)  # Save as JSON
        print(f"\n")
        print(f"{Back.BLACK}{Fore.WHITE}Results saved to {result_file}")  # Notify where results are saved
        print(f"\n")

# Function to remove specified tags from an audio file
def remove_tags(file_path, fields, tag_type):
    try:
        tags = tag_type(file_path)  # Create a tags object for the specified file type
        for field in fields:  # Iterate through each field to remove
            if field in tags:  # Check if the field exists in tags
                del tags[field]  # Delete the field from tags
        tags.save(file_path)  # Save the updated tags back to the file
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Tags removed from {file_path}")  # Notify that tags were removed
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error removing tags from {file_path}: {e}")  # Notify any errors during removal

# Main function to process all audio files in the specified directory
def process_directory(directory, keywords, not_keywords):
    global all_results  # Use the global variable
    folder_count = 0  # Initialize folder count
    file_count = 0  # Initialize file count
    all_results = []  # List to store results for all processed files

    for root, _, files in os.walk(directory):  # Walk through the directory
        folder_count += 1  # Increment folder count
        for file in files:  # Iterate through each file
            file_path = os.path.join(root, file)  # Construct the full file path
            if file.endswith(('.mp3', '.m4a', '.flac', '.wma')):  # Check for specific audio file formats
                file_count += 1  # Increment file count
                print(f"\n")
                print(f"{Back.BLACK}{Fore.WHITE}Processing file: {file_path}")  # Notify which file is being processed

                # Initialize all_tags variable to store tags
                all_tags = None
                results = []  # List to store results for the current file

                # Try to read ID3 tags for MP3 files
                if file.endswith('.mp3'):
                    id3_tags = read_id3_tags(file_path)  # Read ID3 tags
                    ape_tags = read_ape_tags(file_path)  # Read APE tags
                    all_tags = id3_tags or ape_tags  # Combine tags if available
                    
                    if id3_tags and ape_tags:  # Check if both tag types are present
                        print(f"{Back.BLACK}{Fore.WHITE}MP3 file contains both ID3 and APEv2 tags")  # Notify presence of both tags
                        all_tags = {**id3_tags, **ape_tags}  # Merge the tags into a single dictionary
                    elif not all_tags:  # Check if no tags were found
                        print(f"{Back.BLACK}{Fore.WHITE}No ID3 or APE tags found in {file_path}")  # Notify no tags found
                
                # For .m4a files, read MP4 tags
                elif file.endswith('.m4a'):
                    all_tags = read_mp4_tags(file_path)  # Read MP4 tags

                # For other formats, read APEv2 tags
                else:
                    all_tags = read_ape_tags(file_path)  # Read APE tags

                if all_tags:  # If any tags were found
                    results = search_keywords(all_tags, keywords, not_keywords)  # Search for keywords in tags

                    # Store results even if the user interrupts
                    if results:  # If any results were found
                        all_results.append((file_path, results))  # Append results to all_results
                        print(f"{Back.BLACK}{Fore.GREEN}Keywords found in {file_path}:")  # Notify which keywords were found
                        for key, value in results:  # Iterate through each result
                            print(f"{Back.BLACK}{Fore.GREEN}{key}: {value}")  # Print the found key-value pair
                        
                        try:
                            user_input = input("\nIs the detection correct? Please enter 'yes' or 'y' to confirm (or press 'Enter' to skip): ")  # Ask for user confirmation
                            if user_input.lower() in ['yes', 'y']:  # Check if user confirmed
                                remove_tags(file_path, [key for key, _ in results], MP4 if file.endswith('.m4a') else MP3)  # Remove the confirmed tags
                            else:
                                print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping removal of tags.")  # Notify skipping removal

                        except KeyboardInterrupt:  # Catch the Ctrl+C exception
                            print(f"\n{Back.RED}{Fore.WHITE}Script terminated by user (Ctrl+C). Saving results...")  # Notify user of termination
                            save_results("", all_results)  # Save the results before exiting
                            exit(0)  # Exit the script

                else:
                    print(f"{Back.BLACK}{Fore.WHITE}No keywords found in {file_path}")  # Notify no keywords found in file
                
                # Periodically save results after every 10 files
                if len(all_results) % 100 == 0:
                    save_results("", all_results)

    print(f"\n")
    print(f"{Back.BLACK}{Fore.WHITE}Total folders processed: {folder_count}")  # Print total folders processed
    print(f"{Back.BLACK}{Fore.WHITE}Total files processed: {file_count}")  # Print total files processed

    # Save results to a file only after processing all files
    save_results("", all_results)  # Call the function to save results

# Define the directory and keywords for processing
directory = "C:\\Users\\Users\\Desktop\\"  # Specify the directory to process

# Define the list of keywords to search for
keywords = ["https://www."]  # List of keywords

# Define the list of keywords to exclude from search results
not_keywords = ["deezer", "open.spotify", "lame", "discogs", "GENIE", "pmedia_music", "music.apple", "bandcamp", "beatsource", "YOUNG-LUV.COM", "amazon", "beatport", "junodownload"]  # List of excluded keywords

# Process the directory for audio files
process_directory(directory, keywords, not_keywords)  # Call the main function to process the directory
