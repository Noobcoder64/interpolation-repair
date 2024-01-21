
ALGORITHMS = [
    # "INTERPOLATION-MIN-INF",
    # "INTERPOLATION-MIN",
    # "INTERPOLATION-ALLGARS-INF",
    "INTERPOLATION-ALLGARS",
    # "GLASS",
    # "JVTS",
]

FLAGS = " ".join([
    "-allgars",
    # "-min",
    # "-inf",
])

# FLAGS = " ".join([
#     # "-disable-core",
#     # "-disable-record-asm"
# ])

INPUT_PARENT_FOLDER = "inputs/"
# INPUT_PARENT_FOLDER = "inputs-JVTS/"
# INPUT_PARENT_FOLDER = "inputs-interpolation/"
# INPUT_PARENT_FOLDER = "inputs-scalability/"
# INPUT_PARENT_FOLDER = "inputs-scalability-JVTS/"


INPUT_FOLDERS = [
    "SIMPLE",
    # "AMBA-1",
    # "AMBA-2",
    # "SYNTECH15-UNREAL",
    # "SYNTECH15-1UNREAL",
]

# INPUT_FOLDERS = [
#     "addedVarsRG1",
#     "addedVarsLift",
#     "addedVarsHumanoid458",
#     "addedVarsGyro_Var1",
# ]

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
# OUTPUT_PARENT_FOLDER = "outputs-scalability/"
# OUTPUT_PARENT_FOLDER = "outputs-weakness/"
# OUTPUT_PARENT_FOLDER = "outputs-translation/"

RUN = 10

TIMEOUT = 10

REPAIR_LIMIT = 1