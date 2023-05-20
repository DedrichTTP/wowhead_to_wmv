import subprocess
import tempfile
import os
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import pyperclip

# Set the base folder for all exports
##########################################################################################
exportRoot = "Z:/True Potential Dropbox/Share/Houdini_Projects/_WOWLIB/_WMV_Characters/"
##########################################################################################

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

gender_dict = {
    0: "Male",
    1: "Female"
}

# On the left is what wowhead gives, on the right is the WMV correct one
wowhead_wmw_slot_convert_dict = {
    '1': {
            'name': 'Head',
            'wmv': '0'
          },
    '3': {
            'name': 'Shoulders',
            'wmv': '1'
          },
    '16': {
            'name': 'Back',
            'wmv': '11'
          },
    '5': {
            'name': 'Chest',
            'wmv': '6'
          },
    '20': {
            'name': 'Chest',
            'wmv': '6'
          },
    '4': {
            'name': 'Shirt',
            'wmv': '4'
          },
    '19': {
            'name': 'Tabard',
            'wmv': '12'
          },
    '9': {
            'name': 'Wrist',
            'wmv': '7'
          },
    '10': {
            'name': 'Hands',
            'wmv': '8'
          },
    '6': {
            'name': 'Waist',
            'wmv': '3'
          },
    '7': {
            'name': 'Legs',
            'wmv': '5'
          },
    '8': {
            'name': 'Feet',
            'wmv': '2'
          },
    '21': {
            'name': 'Main-Hand',
            'wmv': '9'
          },
    '22': {
            'name': 'Off-Hand',
            'wmv': '10'
          },
    '17': {
            'name': 'Main-Hand',
            'wmv': '9'
          },
    '27': {
            'name': 'Quiver',
            'wmv': '13'
          }
}


# Save JSON file from wowhead link
def get_json_from_url():

    # Prompt the user for the URL
    url = input("Please enter a URL: ")
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with tempfile.TemporaryDirectory() as save_dir:
        print("Gathering data...")
        if("npc" in url):
            try:
                script_path = os.path.join(dir_path, "wowhead_get_json_npc.js")
                subprocess.run(["node", script_path, url, save_dir], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print('Output:', e.output)
                print('Error:', e.stderr)
        else:
            try:
                script_path = os.path.join(dir_path, "wowhead_get_json_dressingRoom.js")
                subprocess.run(["node", script_path, url, save_dir], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print('Output:', e.output.decode('utf-8'))
                print('Error:', e.stderr.decode('utf-8'))


        # define the name of the file to check for
        filename = "data.json"

        # create the full file path
        full_path = os.path.join(save_dir, "data.json")

        # check if the file exists
        if os.path.isfile(full_path):
            jsonFile = open(full_path)
            data = json.load(jsonFile)
            jsonFile.close()
            return data, url
        else:
            print(f"The file {filename} does not exist in the directory {save_dir}.")
            quit()



# Format the JSON file into a common structure
def format_json(jsonData, url):
    if("npc" in url):
        npc = True
    else:
        npc = False

    # Name
    if(npc or "outfit" in url):
        character_name = url.rsplit("/",1)[1].replace("-", " ")
        name_parts = character_name.split()
        character_name = ' '.join(part.capitalize() for part in name_parts)
    else:
        character_name = input("Please enter character name: ")

    # Race / sex information
    if(npc):
        character_gender = gender_dict[jsonData["Gender"]]
        character_race = race_dict[jsonData["Race"]]
    else:
        character_gender = gender_dict[jsonData["charCustomization"]["gender"]]
        character_race = race_dict[jsonData["charCustomization"]["race"]]

    # Customization options
    if(npc):
        character_customization = jsonData["Creature"]["CreatureCustomizations"]
    else:
        character_customization = jsonData["charCustomization"]["options"]

    # Equipment
    if(npc):
        character_equipment = jsonData["Equipment"]
    else:
        character_equipment = {str(item[0]): item[1] for item in jsonData["items"]}
        
    # Generate folder path
    folderPath = os.path.join(exportRoot, character_race + character_gender, character_name)

    # Create folder if it doesn't exist already
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    # Save JSON file
    jsonPath = folderPath + "/" + character_name + ".json"
    
    # Compile a dict with all relevant information  
    character_dict = {
        "jsonPath" : jsonPath,
        "characterInfo" : {
            "name" : character_name,
            "gender" : character_gender,
            "race" : character_race,
            "customization" : character_customization,
            "equipment" : character_equipment
        },   
        "rawData" : jsonData
    }
    
    # Save the character_dict
    with open(jsonPath, 'w') as f:
        json.dump(character_dict, f, indent=4)
    
    def create_url_shortcut(url, title, filepath):
        shortcut = f"""
        [InternetShortcut]
        URL={url}
        """
        with open(filepath, "w") as shortcut_file:
            shortcut_file.write(shortcut)

    create_url_shortcut(url, character_name, jsonPath.replace(".json",".url") )


    print(character_name)
    print(character_race + " " + character_gender)  

    return character_dict


# Generates a CHR file to be imported by WMV based on the JSON file
def generate_chr_xml(character_dict):

    root = ET.Element("SavedCharacter")
    root.set("version", "2.0")

    model = ET.SubElement(root, "model")
    file = ET.SubElement(model, "file")
    modelName = str(character_dict["characterInfo"]["race"]).lower() + str(character_dict["characterInfo"]["gender"]).lower() + "_hd.m2"
    file.set("name", "character/" + character_dict["characterInfo"]["race"] + "/" + str(character_dict["characterInfo"]["gender"]).lower() + "/" + modelName)

    char_details = ET.SubElement(model, "CharDetails")

    CreatureCustomizations = character_dict["characterInfo"]["customization"]
    for customization_data in CreatureCustomizations:
        customization = ET.SubElement(char_details, "customization")
        customization.set("id", str(customization_data['optionId']))
        customization.set("value", str(customization_data['choiceId']))

    
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
            ET.SubElement(item, "slot").set("value", str(wowhead_wmw_slot_convert_dict[slot]["wmv"]))
            ET.SubElement(item, "id").set("value", "-1")
            ET.SubElement(item, "displayId").set("value", str(Equipment[slot]))
            ET.SubElement(item, "level").set("value", "0")
        else:
            print(f"Error: Slot {slot} not found in lookup dict! - {Equipment[slot]}")


    xml_string = ET.tostring(root, "utf-8")
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="    ", newl="\n")
    pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')

    chrFile = character_dict["jsonPath"].replace(".json", ".chr")
    with open(chrFile, 'w') as f:
        f.write(pretty_xml)

    pyperclip.copy(chrFile.replace("/","\\"))
    print(".chr file copied to clipboard, please import into WMV!")



###########EXECUTE############

# Get JSON data
data, url = get_json_from_url()

# Parse JSON data
character_dict = format_json(data, url)

# Generate CHR file
generate_chr_xml(character_dict)