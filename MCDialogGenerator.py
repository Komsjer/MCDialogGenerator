## Komsjer's Dialog generator.
## @Komsjer, Komsjer@kpnmail.nl
## Feel free to edit and use this filter however you like, just attribute me some credit yo.

## Also TexelElf is pretty great. I used his code as an example. http://elemanser.com/filters.html
from pymclevel import TAG_Byte, TAG_Short, TAG_Int, TAG_Compound, TAG_List, TAG_String, TAG_Double, TAG_Float, TAG_Long, TAG_Byte_Array, TAG_Int_Array
from pymclevel import MCSchematic
import inspect
import math
import csv
import re
import os

displayName = "Komsjer's Dialog generator."

inputs = (
  ("Uses:\nFILEPATH\FILENAME.csv for a single file\nFILEPATH to read all files in that folder\nGOOGLESHEET_URL to load a google sheet\n*make sure the sheet is public","label"),
  ("csv_file", ("string","value=C:\\")),
  ("indicator_wool",False),
)
dimensions = 16

def csv_from_url(url):
    import urllib2
    spreadsheet_id = re.findall(r"/([\s\S]*?)/", url)
    spreadsheet_id = max(spreadsheet_id, key=len)
    spreadsheet_grid_id = re.findall(r"gid=(\d+)", url)[0]
    url = "https://docs.google.com/spreadsheets/d/"+spreadsheet_id+"/export?format=csv&id="+spreadsheet_id+"&gid="+spreadsheet_grid_id
    header = {"User-Agent": 'MCChatGenerator'}
    req = urllib2.Request(url, headers = header)

    f = urllib2.urlopen(req)
    return f.read()

class MCDialog:
    def __init__(self, csv_filepath):
        self.identity_name = ""
        self.real_name = ""
        self.npc_color = ""
        self.flavor_text = ""
        self.cord_green_sign = ""
        self.cord_red_sign = ""
        self.aidentity_name = ""
        self.model_type = ""
        self.default_damage = ""
        self.model_rot = ""
        self.audio_target = ""
        self.kill_command = ""
        self.dialog = []
        self.load_csv(csv_filepath)

    def load_csv(self, csv_filepath):
        self.dialog = []
        with open(csv_filepath,"rb") as f:
            reader = csv.reader(f)
            _is_reading = False
            _start_location = -1
            
            for i, dialog_row in enumerate( reader ):
                if i == 1:
                    self.identity_name = dialog_row[0]
                    self.real_name = dialog_row[1]
                    self.npc_color = dialog_row[2]
                    self.flavor_text = dialog_row[3]
                    self.cord_green_sign = dialog_row[4]
                    self.cord_red_sign = dialog_row[5]
                    self.aidentity_name = dialog_row[6]
                    self.model_type = dialog_row[7]
                    self.default_damage = dialog_row[8]
                    self.model_rot = dialog_row[9]
                    self.audio_target = dialog_row[10]
                    self.kill_command = dialog_row[11]
                if str(dialog_row[0]) == "END":
                    _is_reading = False
                    continue

                if str(dialog_row[0]) == "ID":
                    _start_location = i+1
                    _is_reading = True
                    continue

                if str(dialog_row[0]) == "BLANK":
                    self.dialog.append("BLANK")
                    continue

                if str(dialog_row[0]) == "ENDB":
                    self.dialog.append("BLANK")
                    _is_reading = False
                    continue

                if str(dialog_row[0]) == "IGNORE":
                    _start_location+=1
                    continue

                if _is_reading and not (i-_start_location)%3 == 1:
                    dialog_obj = {"id":"", "text":"", "true_text":"", "false_text":"", "sound_call":"","goto":""}
                    dialog_obj["id"] = str(dialog_row[0])
                    dialog_obj["text"] = str(dialog_row[1])
                    dialog_obj["goto"] = re.sub(r"[^0-9]","", str(dialog_row[2] ))
                    dialog_obj["true_text"] = str(dialog_row[3])
                    dialog_obj["false_text"] = str(dialog_row[4])
                    self.dialog.append(dialog_obj)

    def format_tester(self, row_num):
        row = self.dialog[row_num]
        return "/scoreboard players test {0} DateProgress {1} {1}".format(self.identity_name,row["id"] )

    def format_words(self, row_num):
        row = self.dialog[row_num]
        Real_name=self.real_name
        NPC_color=self.npc_color
        Flavor_text=self.flavor_text
        dialogue= row["text"]
        return '/tellraw @a ["",{"text":"<","color":"white"},{"text":"'+Real_name+'","color":"'+NPC_color+'","hoverEvent":{"action":"show_text","value":{"text":"","extra":[{"text":"'+Flavor_text+'"}]}}},{"text":"> ","color":"white"},{"text":"'+dialogue+'","color":"white"}]'

    def format_goto(self, row_num):
        row = self.dialog[row_num]
        return "/scoreboard players set {0} DateProgress {1}".format(self.identity_name,row["goto"])

    def format_sign_true(self, row_num):
        row = self.dialog[row_num]
        Cord_green = self.cord_green_sign
        Identity_name = self.identity_name
        line_text = row["true_text"]
        line_text = line_text.split("/")
        Line_1 = line_text[0] if len(line_text) > 0 else " "
        Line_2 = line_text[1] if len(line_text) > 1 else " "
        Line_3 = line_text[2] if len(line_text) > 2 else " "
        Line_4 = line_text[3] if len(line_text) > 3 else " "
        return '/blockdata '+Cord_green+' {Text1: "{\\"text\\":\\"'+Line_1+'\\",\\"color\\":\\"dark_green\\",\\"bold\\":true,\\"clickEvent\\":{\\"action\\":\\"run_command\\",\\"value\\":\\"/scoreboard players add '+Identity_name+' DateProgress 1\\"}}",Text2: "{\\"text\\":\\"'+Line_2+'\\",\\"color\\":\\"dark_green\\",\\"bold\\":true}",Text3: "{\\"text\\":\\"'+Line_3+'\\",\\"color\\":\\"dark_green\\",\\"bold\\":true}",Text4: "{\\"text\\":\\"'+Line_4+'\\",\\"color\\":\\"dark_green\\",\\"bold\\":true}"}'
    
    def format_sign_false(self, row_num):
        row = self.dialog[row_num]
        Cord_red = self.cord_red_sign
        Identity_name = self.identity_name
        line_text = row["false_text"]
        line_text = line_text.split("/")
        Line_1 = line_text[0] if len(line_text) > 0 else " "
        Line_2 = line_text[1] if len(line_text) > 1 else " "
        Line_3 = line_text[2] if len(line_text) > 2 else " "
        Line_4 = line_text[3] if len(line_text) > 3 else " "
        return '/blockdata '+Cord_red+' {Text1: "{\\"text\\":\\"'+Line_1+'\\",\\"color\\":\\"dark_red\\",\\"bold\\":true,\\"clickEvent\\":{\\"action\\":\\"run_command\\",\\"value\\":\\"/scoreboard players remove '+Identity_name+' DateProgress 1\\"}}",Text2: "{\\"text\\":\\"'+Line_2+'\\",\\"color\\":\\"dark_red\\",\\"bold\\":true}",Text3: "{\\"text\\":\\"'+Line_3+'\\",\\"color\\":\\"dark_red\\",\\"bold\\":true}",Text4: "{\\"text\\":\\"'+Line_4+'\\",\\"color\\":\\"dark_red\\",\\"bold\\":true}"}'
    
    def format_blockdata1(self, row_num):
        row = self.dialog[row_num]
        return "/blockdata ~3 ~ ~ {auto:1b}"

    def format_entity_data(self, row_num):
        row = self.dialog[row_num]
        AIdentity_name = self.aidentity_name
        Model_type = self.model_type
        Default_damage = self.default_damage
        Model_rot = self.model_rot
        return '/entitydata @e[name='+AIdentity_name+'] {ArmorItems:[{},{},{},{id:"'+Model_type+'",Count:1b,Damage:'+Default_damage+'}],Rotation:['+Model_rot+']}'

    def format_killcommand(self,row_num):
        row = self.dialog[row_num]
        KillCommand = self.kill_command
        return "/kill "+KillCommand if KillCommand != "" else ""

    def format_blockdata2(self, row_num):
        row = self.dialog[row_num]
        return "/blockdata ~ ~ ~ {auto:0b}"

    def format_stopsound(self, row_num):
        row = self.dialog[row_num]
        return "/stopsound @a voice"

    def format_execute(self, row_num):
        row = self.dialog[row_num]
        AIdentity_name = self.aidentity_name
        Audio_target = self.audio_target
        ID = row["id"]
        return "/execute @e[name="+AIdentity_name+"] ~ ~ ~ /playsound "+Audio_target+ID+" voice @a[] ~ ~ ~ 1"
    
    def log (self):
        for i in self.dialog:
            print i

def generate_track(dialog,schematic,y=0,indicator_wool=False):
        _indicator_wool_flip_flop = 0
        for i, d in enumerate(dialog.dialog):
            #Blank line
            if d == "BLANK":
                _indicator_wool_flip_flop = 0
                continue

            #Indicator wools
            if indicator_wool:
                if not _indicator_wool_flip_flop:
                    schematic.setBlockAt(0,y+1,i,35)
                    schematic.setBlockDataAt(0,y+1,i, 5)
                    _indicator_wool_flip_flop += 1
                else:
                    schematic.setBlockAt(0,y+1,i,35)
                    schematic.setBlockDataAt(0,y+1,i, 14)
                    _indicator_wool_flip_flop = 0
                    
            #Score check
            schematic.setBlockAt(0,y,i,210)
            schematic.setBlockDataAt(0,y,i, 5)
            schematic.TileEntities.append(CommandBlock(0,y,i,dialog.format_tester(i),False))
            #NPC DIAlogue
            schematic.setBlockAt(1,y,i,211)
            schematic.setBlockDataAt(1,y,i, 13)
            schematic.TileEntities.append(CommandBlock(1,y,i,dialog.format_words(i),True))
            #npc goto
            schematic.setBlockAt(2,y,i,211)
            schematic.setBlockDataAt(2,y,i, 13)
            schematic.TileEntities.append(CommandBlock(2,y,i,dialog.format_goto(i),True))
            #update green sign
            schematic.setBlockAt(3,y,i,211)
            schematic.setBlockDataAt(3,y,i, 13)
            schematic.TileEntities.append(CommandBlock(3,y,i,dialog.format_sign_true(i),True))
            #update red sign
            schematic.setBlockAt(4,y,i,211)
            schematic.setBlockDataAt(4,y,i, 13)
            schematic.TileEntities.append(CommandBlock(4,y,i,dialog.format_sign_false(i),True))
            #blockdata1
            schematic.setBlockAt(5,y,i,211)
            schematic.setBlockDataAt(5,y,i, 13)
            schematic.TileEntities.append(CommandBlock(5,y,i,dialog.format_blockdata1(i),True))
            #format_entity_data
            schematic.setBlockAt(6,y,i,211)
            schematic.setBlockDataAt(6,y,i, 13)
            schematic.TileEntities.append(CommandBlock(6,y,i,dialog.format_entity_data(i),True))
            #format_killcommand
            schematic.setBlockAt(7,y,i,211)
            schematic.setBlockDataAt(7,y,i, 13)
            schematic.TileEntities.append(CommandBlock(7,y,i,dialog.format_killcommand(i),True))
            #format_blockdata2
            schematic.setBlockAt(8,y,i,137)
            schematic.setBlockDataAt(8,y,i, 5)
            schematic.TileEntities.append(CommandBlock(8,y,i,dialog.format_blockdata2(i),False))
            #format_stopsound
            schematic.setBlockAt(9,y,i,211)
            schematic.setBlockDataAt(9,y,i, 5)
            schematic.TileEntities.append(CommandBlock(9,y,i,dialog.format_stopsound(i),True))
            #format_execute
            schematic.setBlockAt(10,y,i,211)
            schematic.setBlockDataAt(10,y,i, 5)
            schematic.TileEntities.append(CommandBlock(10,y,i,dialog.format_execute(i),True))

            

# returns a schematic commandblock TileEntitie tag, code from "ToSummonCommand.py" by TexelElf
def CommandBlock(x,y,z,command, auto = False):
	cmd = TAG_Compound()
	cmd["x"] = TAG_Int(x)
	cmd["y"] = TAG_Int(y)
	cmd["z"] = TAG_Int(z)
	cmd["id"] = TAG_String("Control")
	cmd["Command"] = TAG_String(command)
	cmd["TrackOutput"] = TAG_Byte(0)
	cmd["auto"] = TAG_Byte(1 if auto else 0)
	return cmd


def calculate_schematic_size(dialogs):
    x = 12
    y = 2*len(dialogs)
    z = 0
    for d in dialogs:
        z = len(d.dialog) if len(d.dialog) > z else z
    return (x,y,z)
    

def perform(level, box, options):
    #Gets the editor, taken from code by TexelElf
    editor = inspect.stack()[1][0].f_locals.get('self', None).editor

    #--Options
    csv_file = options["csv_file"]
    indicator_wool = options["indicator_wool"]

    #--Run

    ##Single File
    if os.path.isfile(csv_file) and csv_file.endswith(".csv"):
        print "--PARSING SINGLE FILE--"
        dialog = MCDialog(csv_file)
        dialog.log()
        schematic = MCSchematic(calculate_schematic_size([dialog]), mats=level.materials)
        generate_track(dialog,schematic,indicator_wool=indicator_wool)

    ##Folder
    elif os.path.isdir(csv_file):
        print "--PARSING FOLDER--"
        files = [f for f in os.listdir(csv_file) if f.endswith('.csv')]
        for x in files: print x
        dialogs = [MCDialog(csv_file+"\\"+f) for f in files]
        schematic = MCSchematic(calculate_schematic_size(dialogs), mats=level.materials)
        for j,dialog in enumerate(dialogs):
            generate_track(dialog,schematic,y=j*2 , indicator_wool=indicator_wool)
        if len(dialogs) == 0:
            raise(Exception("No file with extention .csv found in"+csv_file ))
    ##URL
    elif "https://" in csv_file:
        print "--Loading google doc--"
        csv_file = csv_from_url(csv_file)
        full_path = os.path.realpath(__file__)
        path, filename = os.path.split(full_path)
        if not os.path.exists(path+"\.tmp"):
            os.makedirs(path+"\.tmp")
        f = open(path+"\.tmp"+"\dialog.csv" ,"w")
        f.write(csv_file)
        f.close()

        csv_file = path+"\.tmp"+"\dialog.csv"
        dialog = MCDialog(csv_file)
        dialog.log()
        schematic = MCSchematic(calculate_schematic_size([dialog]), mats=level.materials)
        generate_track(dialog,schematic,indicator_wool=indicator_wool)

        
        
        

    else:
        raise(Exception("Couldn't parse path:"+csv_file))

    #Copies the schematic to the editor, taken from code by TexelElf
    editor.addCopiedSchematic(schematic)


    

