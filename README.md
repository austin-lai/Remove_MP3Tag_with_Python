
# Remove MP3Tag with python

```markdown
> Austin.Lai |
> -----------| October 05th, 2024
> -----------| Updated on December 30th, 2024
```

---

## Table of Contents

<!-- TOC -->

- [Remove MP3Tag with python](#remove-mp3tag-with-python)
    - [Table of Contents](#table-of-contents)
    - [Disclaimer](#disclaimer)
    - [Description](#description)
    - [remove-mp3tag-with-python-v1.0](#remove-mp3tag-with-python-v10)

<!-- /TOC -->

<br>

## Disclaimer

<span style="color: red; font-weight: bold;">DISCLAIMER:</span>

This project/repository is provided "as is" and without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

This project/repository is for <span style="color: red; font-weight: bold;">Educational</span> purpose <span style="color: red; font-weight: bold;">ONLY</span>. Do not use it without permission. The usual disclaimer applies, especially the fact that me (Austin) is not liable for any damages caused by direct or indirect use of the information or functionality provided by these programs. The author or any Internet provider bears NO responsibility for content or misuse of these programs or any derivatives thereof. By using these programs you accept the fact that any damage (data loss, system crash, system compromise, etc.) caused by the use of these programs is not Austin responsibility.

<br>

## Description

<!-- Description -->

A small Python project designed to streamline audio file metadata by removing specific fields from ID3v2.4 and APEv2 tags within audio files.

> [!NOTE]
> 
> Features:
> - Targeted environment: Windows, *Nix
> - Support ID3 and APEv2 tags
> - Support FLAC, MP3, WMA and M4A with AAC (Advanced Audio Codec) format files.
> - Python package: `mutagen`, `colorama`.
> - Search audio file metadata by keywords.
> - There are two set of list: `keywords` - the search will search through anything specify inside this list, `not_keywords` - the search will exclude anything specify inside this list.
> - Once keywords that are specified in the `keywords` list, it will display the result to user and prompt the user to enter `'yes' or 'y'` (case-insensitive) to remove the fields out of the audio files or `press 'Enter' to skip`.
> - Save the search result into a json file located at Desktop.
> - Handle script termination when `Ctrl+C` is pressed and save results before exiting.
> - Skip `cover art` and `acoustid fingerprint` field.
> - Show total files and folders that have been processed.

This project is ideal for anyone looking to simplify or automate audio files metadata management.

> [!IMPORTANT]
> Please change the configuration accordingly to suits your environment.

> [!WARNING]
> 🚨 Important Instructions 🚨
> - You may change the conditional in line 80: `if "cover art" in str(key).lower() or "acoustid fingerprint" in str(key).lower():`
> - You may change the value of `directory` in line 384
> - You may change the value of `keywords` in line 387
> - You may change the value of `not_keywords` in line 390

<!-- /Description -->

<br>

## remove-mp3tag-with-python-v1.0

The `remove-mp3tag-with-python-v1.0.py` file can be found [here](remove-mp3tag-with-python-v1.0.py) or below:

<details>

<summary><span style="padding-left:10px;">Click here to expand for the "remove-mp3tag-with-python-v1.0.py" !!!</span></summary>

```python
import os
import re
import signal  # Import signal to handle Ctrl+C interruptions
import json  # Import json to save results in JSON format
from mutagen.id3 import ID3, ID3NoHeaderError, TXXX, COMM  # Import necessary classes for ID3 tags
from mutagen.apev2 import APEv2, APENoHeaderError  # Import necessary classes for APEv2 tags
from mutagen.mp3 import MP3  # Import class for MP3 files
from mutagen.mp4 import MP4  # Import class for MP4 files
from mutagen.flac import FLAC  # Import class for FLAC files
from colorama import init, Fore, Back  # Import colorama for colored terminal output

# Initialize colorama to automatically reset colors after each print
init(autoreset=True)

# Add this global variable at the top of your script to store results
all_results = []

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

# Function to read FLAC tags from FLAC files
def read_flac_tags(file_path):
    try:
        audio = FLAC(file_path)  # Create a FLAC object for the specified file
        tags = audio.tags  # Retrieve the tags from the audio file
        print(f"{Back.BLACK}{Fore.WHITE}Successfully read FLAC tags from {file_path}")  # Notify success
        return tags  # Return the tags
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error reading FLAC tags from {file_path}: {e}")  # Notify any errors
        return None  # Return None on error

# Function to read FLAC tags from FLAC files
def read_mp4_tags(file_path):
    try:
        audio = MP4(file_path)  # Create a MP4 object for the specified file
        tags = audio.tags  # Retrieve the tags from the audio file
        print(f"{Back.BLACK}{Fore.WHITE}Successfully read MP4 tags from {file_path}")  # Notify success
        return tags  # Return the tags
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error reading MP4 tags from {file_path}: {e}")  # Notify any errors
        return None  # Return None on error

# Function to search for keywords in the provided tags
def search_keywords(tags, keywords, not_keywords):
    results = []  # Initialize a list to store found results
    for key, value in tags.items():  # Iterate through each tag

        # Skip "cover art" and "acoustid fingerprint" field
        key_str = str(key).lower()
        if "cover art" in key_str or "cover" in key_str or "acoustid fingerprint" in key_str or "covr" in key_str or "unsyncedlyrics" in key_str or "lyrics" in key_str or "lyr" in key_str or "acoustid_fingerprint" in key_str or "tcon" in key_str or "com.apple.itunes" in key_str or "spotify_release_id" in key_str:
            print(f"Skipping field: {key_str}")  # Debug print to verify exclusion
            continue  # Skip the iteration if the key contains "cover art" and "acoustid fingerprint"
        
        # Convert value to string for comparison
        if isinstance(value, list):
            value_str = " ".join([str(v) for v in value])
        else:
            value_str = str(value)

        value_str = value_str.encode('utf-8', errors='replace').decode('utf-8')

        for keyword in keywords:  # Iterate through each keyword
            # Check if keyword is present and not in not_keywords
            if keyword.lower() in value_str.lower() and not any(nk.lower() in value_str.lower() for nk in not_keywords):
                results.append((key, value))  # Append the found key and value to results
                print(f"{Back.BLACK}{Fore.GREEN}Keyword '{keyword}' found in field '{key}' with value '{value}' (excluding not_keywords)")

    return results  # Return the list of results found

# Function to remove specified tags from an audio file
def remove_tags(file_path, fields):
    try:
        # Detect the file type and create the appropriate tags object
        if file_path.endswith('.mp3'):
            id3_tags = ID3(file_path)
            ape_tags = APEv2(file_path)
            tags_list = [id3_tags, ape_tags]
        elif file_path.endswith('.m4a'):
            mp4_tags = MP4(file_path)
            id3_tags = ID3(file_path)
            ape_tags = APEv2(file_path)
            tags_list = [mp4_tags,id3_tags, ape_tags]
        elif file_path.endswith('.flac'):
            flac_tags = FLAC(file_path)
            tags_list = [flac_tags]
        elif file_path.endswith('.wma'):
            mp4_tags = MP4(file_path)
            id3_tags = ID3(file_path)
            ape_tags = APEv2(file_path)
            tags_list = [mp4_tags,id3_tags, ape_tags]
        else:
            print(f"{Back.RED}{Fore.WHITE}Unsupported file type: {file_path}")
            return

        print(f"{Back.BLACK}{Fore.LIGHTYELLOW_EX}\nFields to remove: {fields}")  # Debug print to show fields to be removed

        for tags in tags_list:
            print(f"{Back.BLACK}{Fore.LIGHTYELLOW_EX}\nInitial tags for {file_path}: {tags.keys()}\n")  # Debug print to show initial tag keys

            for field in fields:  # Iterate through each field to remove
                found = False
                for tag_key in tags.keys():
                    if field.lower() in tag_key.lower():  # Check if the field exists in tags
                        print(f"{Back.BLACK}{Fore.LIGHTYELLOW_EX}Removing field: {tag_key}")  # Debug print to show field being removed
                        del tags[tag_key]  # Delete the field from tags
                        found = True
                        break
                if not found:
                    print(f"{Back.RED}{Fore.WHITE}Field not found: {field}")  # Debug print to show field not found

            tags.save(file_path)  # Save the updated tags back to the file
            print(f"{Back.BLACK}{Fore.LIGHTRED_EX}\nTags removed from {file_path}")  # Notify that tags were removed
            print(f"{Back.BLACK}{Fore.WHITE}\nUpdated tags for {file_path}: {tags.keys()}")  # Debug print to show updated tag keys
    except Exception as e:
        print(f"{Back.RED}{Fore.WHITE}Error removing tags from {file_path}: {e}")  # Notify any errors during removal

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

# Main function to process all audio files in the specified directory
def process_directory(directory, keywords, not_keywords):
    
    folder_count = 0  # Initialize folder count
    file_count = 0  # Initialize file count

    update_script(directory, keywords, not_keywords)

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

                # For .flac files, read FLAC tags
                elif file.endswith('.flac'):
                    all_tags = read_flac_tags(file_path)  # Read FLAC tags

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
                                remove_tags(file_path, [key for key, _ in results])  # Remove the confirmed tags
                            else:
                                print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping removal of tags.")  # Notify skipping removal

                        except KeyboardInterrupt:  # Catch the Ctrl+C exception
                            print(f"\n{Back.RED}{Fore.WHITE}Script terminated by user (Ctrl+C). Saving results...")  # Notify user of termination
                            save_results("", all_results)  # Save the results before exiting
                            exit(0)  # Exit the script

                else:
                    print(f"{Back.BLACK}{Fore.WHITE}No keywords found in {file_path}")  # Notify no keywords found in file
                
                # Periodically save results after every 100 files
                if len(all_results) % 100 == 0:
                    save_results("", all_results)

    print(f"\n")
    print(f"{Back.BLACK}{Fore.WHITE}Total folders processed: {folder_count}")  # Print total folders processed
    print(f"{Back.BLACK}{Fore.WHITE}Total files processed: {file_count}")  # Print total files processed

    # Save results to a file only after processing all files
    save_results("", all_results)  # Call the function to save results

# Function to modify directory if user wants to change it
def modify_directory(directory):
    print(f"{Back.BLACK}{Fore.WHITE}\nCurrent directory: \t{directory}")
    change_dir = input("Do you want to change the directory? Please enter 'yes' or 'y' to confirm (or press 'Enter' to skip): ").strip().lower()
    
    if change_dir in ["yes", "y"]:
        new_dir = input("Enter new directory: ").strip()
        directory = new_dir.replace("\\", "\\\\")  # Handle Windows paths with double backslashes
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Directory changed to: \t{directory}")
    else:
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping changing directory.")  # Notify changing directory

    return directory

# Function to modify keywords if user wants to add/remove them
def modify_keywords(keywords):
    print(f"{Back.BLACK}{Fore.WHITE}\n\nCurrent keywords: {keywords}")
    
    change_kw = input("\nDo you want to add more keywords? Please enter 'yes' or 'y' to confirm (or press 'Enter' to skip): ").strip().lower()
    
    if change_kw in ["yes", "y"]:
        additional_kw = input("Enter keywords to add (comma separated): ").strip().split(',')
        keywords.extend([kw.strip() for kw in additional_kw if kw.strip()])  # Add new keywords

        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}\nUpdated keywords: {keywords}")
    else:
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping adding keywords.")  # Notify adding keywords
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Updated keywords: {keywords}")

    remove_kw = input("\nDo you want to remove any keywords? Please enter 'yes' or 'y' to confirm (or press 'Enter' to skip): ").strip().lower()
    
    if remove_kw in ["yes", "y"]:
        removal_kw = input("Enter keywords to remove (comma separated): ").strip().split(',')
        keywords = [kw for kw in keywords if kw not in removal_kw]  # Remove specified keywords
        
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}\nUpdated keywords: {keywords}")
    else:
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping removing keywords.")  # Notify removing keywords
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Updated keywords: {keywords}")

    return keywords

# Function to modify not_keywords if user wants to add/remove them
def modify_not_keywords(not_keywords):
    print(f"{Back.BLACK}{Fore.WHITE}\n\nCurrent not_keywords: {not_keywords}")
    
    change_nkw = input("\nDo you want to add more not_keywords? Please enter 'yes' or 'y' to confirm (or press 'Enter' to skip): ").strip().lower()
    
    if change_nkw in ["yes", "y"]:
        additional_nkw = input("Enter not_keywords to add (comma separated): ").strip().split(',')
        not_keywords.extend([nkw.strip() for nkw in additional_nkw if nkw.strip()])  # Add new not_keywords

        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}\nUpdated not_keywords: {not_keywords}")
    else:
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping adding not_keywords.")  # Notify adding not_keywords
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Updated not_keywords: {not_keywords}")
    
    remove_nkw = input("\nDo you want to remove any not_keywords? Please enter 'yes' or 'y' to confirm (or press 'Enter' to skip): ").strip().lower()
    
    if remove_nkw in ["yes", "y"]:
        removal_nkw = input("Enter not_keywords to remove (comma separated): ").strip().split(',')
        not_keywords = [nkw for nkw in not_keywords if nkw not in removal_nkw]  # Remove specified not_keywords
    
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}\nUpdated not_keywords: {not_keywords}")
    else:
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Skipping removing not_keywords.")  # Notify removing keywords
        print(f"{Back.BLACK}{Fore.LIGHTRED_EX}Updated not_keywords: {not_keywords}")
    
    return not_keywords

# Function to update the Python script with new values
def update_script(directory, keywords, not_keywords):

    # Store original values to compare later
    original_directory = directory
    original_keywords = keywords[:]
    original_not_keywords = not_keywords[:]

    directory = modify_directory(directory)  # Allow the user to modify the directory
    keywords = modify_keywords(keywords)  # Allow the user to modify the keywords
    not_keywords = modify_not_keywords(not_keywords)  # Allow the user to modify the not_keywords

    script_file = __file__  # Get the current script file name
    
    # Read the current script contents
    with open(script_file, 'r', encoding='utf-8') as f:
        script_contents = f.read()

    # Check if any changes were made before calling update_script()
    if directory != original_directory or keywords != original_keywords or not_keywords != original_not_keywords:
        
        # Update the directory
        if directory != original_directory:

            directory_pattern = r'(# Define the directory and keywords for processing\s*\n\s*directory\s*=\s*")(.*?)(")'

            new_directory_value = f'{directory.replace("\\", "\\\\")}'  # Properly escape backslashes

            script_contents = re.sub(directory_pattern, r'\1' + new_directory_value + r'\3', script_contents)

            # Write the updated script back
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_contents)
            print(f"\n")
            print(f"{Back.GREEN}{Fore.WHITE}Script updated with new directory values.")

        # Update the keywords
        if keywords != original_keywords:

            keywords_pattern = r'(# Define the list of keywords to search for\s*\n\s*keywords\s*=\s*\[)([^\]]*)(\])'

            new_keywords_value = ", ".join([f'"{k}"' for k in keywords])  # Format keywords as a list of strings
            
            script_contents = re.sub(keywords_pattern, r'\1' + new_keywords_value + r'\3', script_contents)

            # Write the updated script back
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_contents)
            print(f"\n")
            print(f"{Back.GREEN}{Fore.WHITE}Script updated with new keywords values.")

        # Update the not_keywords
        if not_keywords != original_not_keywords:

            not_keywords_pattern = r'(# Define the list of keywords to exclude from search results\s*\n\s*not_keywords\s*=\s*\[)([^\]]*)(\])'

            new_not_keywords_value = ", ".join([f'"{nk}"' for nk in not_keywords])  # Format not_keywords as a list of strings

            script_contents = re.sub(not_keywords_pattern, r'\1' + new_not_keywords_value + r'\3', script_contents)
        
            # Write the updated script back
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_contents)
            print(f"\n")
            print(f"{Back.GREEN}{Fore.WHITE}Script updated with new not_keywords values.")

    else:
        print(f"\n")
        print(f"{Back.GREEN}{Fore.WHITE}No changes made, skipping script update.")



# Main execution
if __name__ == "__main__":

    # Define the directory and keywords for processing
    directory = "C:\\Users\\Users\\Desktop\\"  # Specify the directory to process

    # Define the list of keywords to search for
    keywords = ["https://www."]  # List of keywords

    # Define the list of keywords to exclude from search results
    not_keywords = ["deezer", "open.spotify", "lame", "discogs", "GENIE", "pmedia_music", "music.apple", "bandcamp", "beatsource", "YOUNG-LUV.COM", "amazon", "beatport", "junodownload", "WWW.APPLE.COM"]  # List of excluded keywords

    # Process the directory for audio files
    process_directory(directory, keywords, not_keywords)  # Call the main function to process the directory

```

</details>


