import subprocess
import os
import sys
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import pyperclip
import settings
from urllib.parse import urlparse
import shutil
import tempfile
import re

# Get the current script location
rel_script_path = os.path.dirname(os.path.realpath(__file__))

# Check if settings.py file exists
if not os.path.exists(os.path.join(rel_script_path, 'settings.py')):
    print("Settings.py file does not exist!")
    sys.exit()

if settings.saveDir is None or settings.saveDir == "":
    print("Save dir is empty! Please update settings.py")
    sys.exit()
else:
    saveDir = settings.saveDir.replace("\\", "/")
    if saveDir[-1] == "/":
        saveDir = saveDir[:-1]

# Check if directory exists
if not os.path.exists(saveDir):
    print(f"Directory '{saveDir}' does not exist!")
    sys.exit()

# Check if directory is writable
if not os.access(saveDir, os.W_OK):
    print(f"Directory '{saveDir}' is not writable!")
    sys.exit()

print(f"Directory set to: {saveDir}\n")


race_dict = {
    1: "human",
    2: "orc",
    3: "dwarf",
    4: "nightelf",
    5: "scourge",
    6: "tauren",
    7: "gnome",
    8: "troll",
    9: "goblin",
    10: "bloodelf",
    11: "draenei",
    12: "felorc",
    13: "naga_",
    14: "broken",
    15: "skeleton",
    16: "vrykul",
    17: "tuskarr",
    18: "foresttroll",
    19: "taunka",
    20: "northrendskeleton",
    21: "icetroll",
    22: "worgen",
    23: "human",
    24: "pandaren",
    25: "pandaren",
    26: "pandaren",
    27: "nightborne",
    28: "highmountaintauren",
    29: "voidelf",
    30: "lightforgeddraenei",
    31: "zandalaritroll",
    32: "kultiran",
    33: "thinhuman",
    34: "darkirondwarf",
    35: "vulpera",
    36: "magharorc",
    37: "mechagnome",
    52: "dracthyr",
    70: "dracthyr",
}

gender_dict = {0: "Male", 1: "Female"}

noHdModels = [
    "brokenfemale",
    "brokenmale",
    "companiondrake",
    "companionprotodragon",
    "companionpterrodax",
    "companionserpent",
    "companionwyvern",
    "darkirondwarffemale",
    "darkirondwarfmale",
    "dracthyrdragon",
    "dracthyrfemale",
    "dracthyrmale",
    "felorcfemale",
    "felorcmale",
    "felorcmaleaxe",
    "felorcmalesword",
    "foresttrollmale",
    "goblinfemale",
    "goblinmale",
    "highmountaintaurenfemale",
    "highmountaintaurenmale",
    "icetrollmale",
    "kultiranfemale",
    "kultiranmale",
    "lightforgeddraeneifemale",
    "lightforgeddraeneimale",
    "mechagnomefemale",
    "mechagnomemale",
    "naga_female",
    "naga_male",
    "nightbornefemale",
    "nightbornemale",
    "northrendskeletonmale",
    "orcmaleupright",
    "pandarenfemale",
    "pandarenmale",
    "skeletonfemale",
    "skeletonmale",
    "taunkamale",
    "thinhumanmale",
    "voidelffemale",
    "voidelfmale",
    "vrykulmale",
    "vulperafemale",
    "vulperamale",
    "worgenfemale",
    "worgenmale",
    "zandalaritrollfemale",
    "zandalaritrollmale",
]

# On the left is what wowhead gives, on the right is the WMV correct one
wowhead_wmw_slot_convert_dict = {
    "1": {"name": "Head", "wmv": "0"},
    "3": {"name": "Shoulders", "wmv": "1"},
    "16": {"name": "Back", "wmv": "11"},
    "5": {"name": "Chest", "wmv": "6"},
    "20": {"name": "Chest", "wmv": "6"},
    "4": {"name": "Shirt", "wmv": "4"},
    "19": {"name": "Tabard", "wmv": "12"},
    "9": {"name": "Wrist", "wmv": "7"},
    "10": {"name": "Hands", "wmv": "8"},
    "6": {"name": "Waist", "wmv": "3"},
    "7": {"name": "Legs", "wmv": "5"},
    "8": {"name": "Feet", "wmv": "2"},
    "21": {"name": "Main-Hand", "wmv": "9"},
    "17": {"name": "Main-Hand", "wmv": "9"},
    "15": {"name": "Main-Hand", "wmv": "9"},
    "22": {"name": "Off-Hand", "wmv": "10"},
    "14": {"name": "Off-Hand", "wmv": "10"},
    "27": {"name": "Quiver", "wmv": "13"},
}

# Run node.js with output
def run_script_and_print_output(script_path, url, save_dir):
    # Start the process
    process = subprocess.Popen(
        ["node", script_path, url, save_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Use a loop to read the output line by line
    while True:
        output = process.stdout.readline()

        # Break the loop if the process is done
        if process.poll() is not None:
            break

        # Print the output
        if output:
            print(output.strip())

    # Print any output that's left
    remainder = process.communicate()[0]
    if remainder:
        print(remainder.strip())

    return process


# Gather JSON and texture data from wowhead
def get_json_from_url(tmpdir):

    # Prompt the user for the URL
    url = input("Please enter a URL: ")
    parsed_url = urlparse(url)

    if not (parsed_url.scheme and parsed_url.netloc):
        print("Invalid URL")
        sys.exit()

    # Strip any other stuff from NPC views
    if "npc" in url or "outfit" in url:
        url = url.split("#", 1)[0] + "#modelviewer"

    # Create relative path to current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    if "npc" in url:
        try:
            script_path = os.path.join(dir_path, "wowhead_get_json_npc.js")
            result = run_script_and_print_output(script_path, url, tmpdir)
        except subprocess.CalledProcessError as e:
            print("Output:", e.output)
            print("Error:", e.stderr)
            print(result.stdout)
    else:
        try:
            script_path = os.path.join(
                dir_path, "wowhead_get_json_dressingRoom.js")
            result = run_script_and_print_output(script_path, url, tmpdir)
        except subprocess.CalledProcessError as e:
            print("Output:", e.output.decode("utf-8"))
            print("Error:", e.stderr.decode("utf-8"))

    if result is None:
        print("NONE ERRORING!!AHHHHH")
        sys.exit()

    # define the name of the file to check for
    filename = "data.json"

    # create the full file path
    full_path = os.path.join(tmpdir, "data.json")

    # check if the file exists
    if os.path.isfile(full_path):
        jsonFile = open(full_path)
        data = json.load(jsonFile)
        jsonFile.close()
        return data, url
    else:
        print(
            f"The file {filename} does not exist in the directory {tmpdir}.")
        quit()

    # copy the images


# Format the JSON file into a common structure
def format_json(jsonData, url, tmpdir):
    # Name
    if "npc" in url:
        character_name = (
            url.rsplit("/", 1)[1].replace("-", " ").replace("#modelviewer", "")
        )
        name_parts = character_name.split()
        character_name = " ".join(part.capitalize() for part in name_parts)
        
        character_gender = gender_dict[jsonData["Character"]["Gender"]]
        character_race = race_dict[jsonData["Character"]["Race"]]

        character_customization = jsonData["Creature"]["CreatureCustomizations"]

        character_equipment = jsonData["Equipment"]
    else:
        if "outfit" in url:
            character_name = (
                url.rsplit("/", 1)[1].replace("-",
                                              " ").replace("#modelviewer", "")
            )
        else:
            character_name = input("Please enter character name: ")

        character_gender = gender_dict[jsonData["charCustomization"]["gender"]]
        character_race = race_dict[jsonData["charCustomization"]["race"]]

        if character_name == '':
                print("No name entered, autonaming...")
                autoName = character_race + character_gender
                folderTempPath = os.path.join(saveDir, autoName)
                try:
                    all_entries = os.listdir(folderTempPath)
                    matching_folders = [entry for entry in all_entries if os.path.isdir(os.path.join(folderTempPath, entry)) and entry.startswith(autoName + "_")]
                    numbers = [int(re.search(r'(\d+)$', folder).group(1)) for folder in matching_folders if re.search(r'(\d+)$', folder)]
                    highest_number = max(numbers, default=0)
                except:
                    print("no folder exists, creating one")
                    os.mkdir(folderTempPath)
                    highest_number = 0
                    
                character_name = f"{autoName}_{highest_number + 1:02}"
                


        character_customization = jsonData["charCustomization"]["options"]

        character_equipment = {str(item[0]): item[1]
                               for item in jsonData["items"]}

    # Set export folder path
    folderPath = os.path.join(
        saveDir, character_race + character_gender, character_name
    ).replace("\\", "/")

    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    # Set image export folder path
    imageFolderPath = os.path.join(
        saveDir, character_race + character_gender, character_name + "/tex"
    ).replace("\\", "/")

    if not os.path.exists(imageFolderPath):
        os.makedirs(imageFolderPath)

    # Save JSON file
    jsonPath = folderPath + "/" + character_name + ".json"

    # Get a list of all files in the tmp directory
    if "npc" not in url:
        src_images = (os.path.join(tmpdir, "images"))
        files = os.listdir(src_images)

        # Move each file to the destination directory
        for file in files:
            old_file_path = os.path.join(src_images, file)

            try:
                shutil.copy2(os.path.join(old_file_path), imageFolderPath)

            except Exception as e:
                print(f"Warning: {str(e)}")
                continue

    # Compile a dict with all relevant information
    character_dict = {
        "jsonPath": jsonPath,
        "characterInfo": {
            "name": character_name,
            "gender": character_gender,
            "race": character_race,
            "customization": character_customization,
            "equipment": character_equipment,
        },
        "rawData": jsonData,
    }

    if "npc" in url:
        character_dict["characterInfo"]["type"] = "npc"
    elif "outfit" in url:
        character_dict["characterInfo"]["type"] = "outfit"
    else:
        character_dict["characterInfo"]["type"] = "custom"

    # Save the character_dict
    with open(jsonPath, "w") as f:
        json.dump(character_dict, f, indent=4)

    def create_url_shortcut(url, title, filepath):
        shortcut = f"""
        [InternetShortcut]
        URL={url}
        """
        with open(filepath, "w") as shortcut_file:
            shortcut_file.write(shortcut)

    create_url_shortcut(url, character_name, jsonPath.replace(".json", ".url"))

    def create_bat_file(save_path):
        bat_script = """
        @echo off
        for /R %%i in (*.chr) do (
            echo %%~fi | clip
            goto :eof
        )
        """
        with open(save_path, "w") as bat_file:
            bat_file.write(bat_script)

    print("\n" + character_name)
    print(character_race + " " + character_gender + "\n")

    # Generate screenshot
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, "generate_screenshot.js")
    screenshot_path = folderPath + "\\" + character_name + ".jpg"
    if character_dict["characterInfo"]["type"] == "outfit":
        print("Outfits not currently supported for screenshots!")
    else:
        print("Generating screenshot...")
        if "npc" in url:
            url += "#modelviewer"
        try:
            subprocess.run(
                [
                    "node",
                    script_path,
                    url,
                    screenshot_path,
                    character_dict["characterInfo"]["type"],
                ],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(e.stderr)

    # Create a bat file for copying the .chr file
    create_bat_file(folderPath + "\\" + "copy CHR to clipboard.bat")
    return character_dict


# Generates a CHR file to be imported by WMV based on the JSON file
def generate_chr_xml(character_dict):

    root = ET.Element("SavedCharacter")
    root.set("version", "2.0")

    model = ET.SubElement(root, "model")
    file = ET.SubElement(model, "file")

    modelName = (
        str(character_dict["characterInfo"]["race"]).lower()
        + str(character_dict["characterInfo"]["gender"]).lower()
    )
    if modelName not in noHdModels:
        modelName += "_hd.m2"
    else:
        modelName += ".m2"

    file.set(
        "name",
        "character/"
        + character_dict["characterInfo"]["race"]
        + "/"
        + str(character_dict["characterInfo"]["gender"]).lower()
        + "/"
        + modelName,
    )

    char_details = ET.SubElement(model, "CharDetails")

    CreatureCustomizations = character_dict["characterInfo"]["customization"]
    for customization_data in CreatureCustomizations:
        customization = ET.SubElement(char_details, "customization")
        customization.set("id", str(customization_data["optionId"]))
        customization.set("value", str(customization_data["choiceId"]))

    # Add other static customizations
    ET.SubElement(char_details, "eyeGlowType").set("value", "1")
    ET.SubElement(char_details, "showUnderwear").set("value", "0")
    ET.SubElement(char_details, "showEars").set("value", "1")
    ET.SubElement(char_details, "showHair").set("value", "1")
    ET.SubElement(char_details, "showFacialHair").set("value", "1")
    ET.SubElement(char_details, "showFeet").set("value", "0")
    ET.SubElement(char_details, "isDemonHunter").set("value", "0")

    equipment = ET.SubElement(root, "equipment")

    Equipment = character_dict["characterInfo"]["equipment"]
    for slot in Equipment:
        if slot in wowhead_wmw_slot_convert_dict:
            item = ET.SubElement(equipment, "item")
            ET.SubElement(item, "slot").set(
                "value", str(wowhead_wmw_slot_convert_dict[slot]["wmv"])
            )
            ET.SubElement(item, "id").set("value", "-1")
            ET.SubElement(item, "displayId").set("value", str(Equipment[slot]))
            ET.SubElement(item, "level").set("value", "0")
        else:
            print(
                f"Error: Slot {slot} not found in lookup table! - {Equipment[slot]}")

    xml_string = ET.tostring(root, "utf-8")
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="    ", newl="\n")
    pretty_xml = pretty_xml.replace(
        '<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>'
    )

    chrFile = character_dict["jsonPath"].replace(".json", ".chr")
    with open(chrFile, "w") as f:
        f.write(pretty_xml)

    pyperclip.copy(chrFile.replace("/", "\\"))
    print(".chr file copied to clipboard, please import into WMV!")


########### EXECUTE############
with tempfile.TemporaryDirectory() as tmpdir:
    # Get JSON data
    data, url = get_json_from_url(tmpdir)

    # Parse JSON data
    character_dict = format_json(data, url, tmpdir)

    # Generate CHR file
    generate_chr_xml(character_dict)
