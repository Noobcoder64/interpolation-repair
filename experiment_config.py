
# List of input folders
INPUT_FOLDERS = [
    "inputs/SIMPLE",
    "inputs/AMBA",
    "Examples/AMBAs",
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
    "INTERPOLATION-MIN-INF",
    # "INTERPOLATION-MIN",
    # "INTERPOLATION-ALLGARS-INF",
    # "INTERPOLATION-ALLGARS",
    # "INTERPOLATION-NOSYS",
    # "GLASS",
    # "JVTS",
]

SYSTEMS = [
    "amba",
    "ColorSort",
    "Gyro",
    "Humanoid",
    "PCar",
]

# Output parent folder
OUTPUT_PARENT_FOLDER = "outputs/"
# OUTPUT_PARENT_FOLDER = "outputs-interpolation/"
# OUTPUT_PARENT_FOLDER = "outputs-symbolic/"
# OUTPUT_PARENT_FOLDER = "outputs-weakness/"
# OUTPUT_PARENT_FOLDER = "outputs-translation/"

# Set the timeout
TIMEOUT = 10