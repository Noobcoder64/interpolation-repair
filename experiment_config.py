
# List of algorithms
ALGORITHMS = [
    # "INTERPOLATION-MIN-INF",
    # "INTERPOLATION-MIN",
    # "INTERPOLATION-ALLGARS-INF",
    # "INTERPOLATION-ALLGARS",
    # "GLASS",
    "JVTS",
]

FLAGS = " ".join([
    # "-allgars",
    # "-min",
    # "-inf",
])

# List of input folders
INPUT_FOLDERS = [
    # "inputs/SIMPLE",
    # "inputs/AMBA-1",
    # "inputs/AMBA-2",
    "inputs/SYNTECH15-UNREAL",
    # "inputs/SYNTECH15-1UNREAL",
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

RUN = 1

# Set the timeout
TIMEOUT = 10