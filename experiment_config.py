
# List of input folders
INPUT_FOLDERS = [
    # "inputs/AMBA",
    # "inputs/SYNTECH15-UNREAL",
    # "inputs/SYNTECH15-1UNREAL",
    
    "inputs-translation/SYNTECH15-UNREAL-ORIGINAL",
    "inputs-translation/SYNTECH15-UNREAL-TRANSLATED-1",
    "inputs-translation/SYNTECH15-UNREAL-TRANSLATED-2",

]

# List of algorithms
ALGORITHMS = [
    # "INTERPOLATION-NONINF",
    # "INTERPOLATION-ALLGARS",
    # "INTERPOLATION-MIN",
    # "INTERPOLATION",
    "GLASS",
    "JVTS",
    # "ALUR",
]

SYSTEMS = [
    "amba",
    "ColorSort",
    "Gyro",
    "Humanoid",
    "PCar",
]

# Output parent folder
# OUTPUT_PARENT_FOLDER = "outputs/"
OUTPUT_PARENT_FOLDER = "outputs-translation/"

# Set the timeout
TIMEOUT = 10