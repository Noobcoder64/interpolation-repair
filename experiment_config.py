
# List of algorithms
ALGORITHMS = [
    "INTERPOLATION-MIN-INF",
    # "INTERPOLATION-MIN",
    # "INTERPOLATION-ALLGARS-INF",
    # "INTERPOLATION-ALLGARS",
    # "GLASS",
    # "JVTS",
]

FLAGS = " ".join([
    # "-allgars",
    "-min",
    "-inf",
])

# INPUT_PARENT_FOLDER = "inputs/"
INPUT_PARENT_FOLDER = "inputs-interpolation/"

# List of input folders
INPUT_FOLDERS = [
    "SIMPLE",
    # "inputs/AMBA-1",
    "AMBA-2",
    "SYNTECH15-UNREAL",
    "SYNTECH15-1UNREAL",
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
OUTPUT_PARENT_FOLDER = "outputs-interpolation/"
# OUTPUT_PARENT_FOLDER = "outputs-symbolic/"
# OUTPUT_PARENT_FOLDER = "outputs-weakness/"
# OUTPUT_PARENT_FOLDER = "outputs-translation/"

RUN = 10

# Set the timeout
TIMEOUT = 10

REPAIR_LIMIT = 1