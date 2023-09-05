
# List of input folders
INPUT_FOLDERS = [
    "inputs/AMBA",
    "inputs/SYNTECH15-UNREAL",
    "inputs/SYNTECH15-1UNREAL",
    # "inputs/AMBA-ORIGINAL",
    # "inputs/SYNTECH15-UNREAL-ORIGINAL",
    # "inputs/SYNTECH15-1UNREAL-ORIGINAL",
    # "inputs/ENUM-ORIGINAL-G",
    # "inputs/ENUM-ORIGINAL-ALW",
    # "inputs/ENUM-TRANSLATED-G",
    # "inputs/ENUM-TRANSLATED-ALW",
    # "inputs/BOOL-TRANSLATED-G",
]

# List of algorithms
ALGORITHMS = [
    # "INTERPOLATION-MIN-INF",
    # "INTERPOLATION-MIN",
    # "INTERPOLATION-ALLGARS-INF",
    # "INTERPOLATION-ALLGARS",
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
# OUTPUT_PARENT_FOLDER = "outputs-interpolation/"
OUTPUT_PARENT_FOLDER = "outputs-symbolic/"

# Set the timeout
TIMEOUT = 10