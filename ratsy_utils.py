import marduk as mdk # Old videogame quote
import specification as s
import winning_region as wr
import xml.etree.ElementTree as ET
import xml.dom.minidom as mdom
from models.entries import SignalsModel, RequirementsModel
from models.game import GameLogicModel
from spec_debug.path_finder import PathFinder
from spec_debug.spec_debug_utils import SpecDebugUtils
from nusmv import dd
from bddwrap import BDD
import bddwrap
import marduk_utils
import cmd2
import io_utils as io

def readRATFile(filename):
    """Reads a specification XML tree from .rat filename"""
    return ET.parse(filename)

def writeRATFile(filename,tree):
    """Writes an XML specification to a .rat file"""
    f = open(filename, "w")
    tree.write(filename)
    f.close()


def addRequirement(tree,reqname,reqproperty,reqkind,reqtoggled):
    """Adds a requirement to a specification"""
    reqs = tree.getroot().find('requirements')
    new_req = ET.SubElement(reqs, 'requirement')
    ET.SubElement(new_req, 'name').text = reqname
    ET.SubElement(new_req, 'property').text = reqproperty
    ET.SubElement(new_req, 'kind').text = reqkind
    ET.SubElement(new_req, 'base_automaton_name')
    ET.SubElement(new_req, 'notes')
    ET.SubElement(new_req, 'toggled').text = reqtoggled
    return tree

def getRequirementFromName(tree,reqname):
    """Returns the logical expression of the requirement (assumption or guarantee) given a name"""
    reqs = tree.getroot().find('requirements')
    for req in reqs.iter('requirement'):
        if req.find('name').text==reqname:
            return io.normalizeFormulaSyntax(req.find('property').text)
    return None

def toggleRequirement(tree,reqname):
    """Toggles the requirement reqname in filename"""
    reqs = tree.getroot().find('requirements')
    for req in reqs.iter('requirement'):
        if req.find('name').text==reqname:
            req.find('toggled').text = "1"
            return tree
    return tree

def untoggleRequirement(tree,reqname):
    """Untoggles the requirement reqname in tree"""
    reqs = tree.getroot().find('requirements')
    for req in reqs.iter('requirement'):
        if req.find('name').text==reqname:
            req.find('toggled').text = "0"
            return tree
    return tree

def toggleUnrealizableCore(tree,unreal_core_names):
    """Toggles all guarantees in the unrealizable core and untoggles the other guarantees"""
    reqs = tree.getroot().find('requirements')
    for req in reqs.iter('requirement'):
        if "A" in req.find('kind').text or req.find('name').text in unreal_core_names:
            req.find('toggled').text = "1"
        else:
            req.find('toggled').text = "0"
    return tree

def removeRequirement(tree,reqname):
    reqs = tree.getroot().find('requirements')
    for req in reqs.iter('requirement'):
        if req.find('name').text == reqname:
            reqs.remove(req)
            return tree
    return tree

def extractGuaranteeNames(reqs_tree):
    guaranteesList = []

    # The LTL formula of an assumption unit is in the <requirement> element
    for req in reqs_tree.getroot().find("requirements").iter("requirement"):
        # The <kind> node contains the requirement type (A or G)
        # The <name> node contains the id of the formula
        if req.find('kind').text == "G":
            guaranteesList.append(req.find('name').text)

    return guaranteesList

def initMarduk(specfile):
    """Initializes a Marduk object"""
    marduk_options = mdk.MardukOptions()
    marduk_options.input_file = specfile
    marduk_options.verbose = 0
    marduk_options.dyn_reorder = True
    marduk_options.reorder1 = True
    marduk_options.reorder2 = True
    marduk = mdk.Marduk(marduk_options, None)

    # This reads an XML spec and creates a variable list for marduk
    marduk.specification = s.Specification(marduk)
    marduk.specification.readSpecification()
    marduk.vars = marduk.specification.create_variable_list()

    # Addition for this wrapper: vars need to be accessed by name.
    # Adding a dictionary for this
    marduk.vars_dict = dict()
    for var in marduk.vars:
        marduk.vars_dict[var.name] = var

    marduk.spec_debug_utils = SpecDebugUtils(marduk)

    return marduk

def getNewMardukVariable(marduk, varname):
    # Assuming the spec_debug_utils object is in a consistent state with marduk
    bdd_ps_ptr = dd.bdd_new_var(marduk.dd_mgr)
    present = BDD(bdd_ps_ptr, marduk.dd_mgr, varname + "_ps")
    dd.bdd_free(marduk.dd_mgr, bdd_ps_ptr)
    bdd_ns_ptr = dd.bdd_new_var(marduk.dd_mgr)
    next = BDD(bdd_ns_ptr, marduk.dd_mgr, varname + "_ns")
    dd.bdd_free(marduk.dd_mgr, bdd_ns_ptr)

    var = marduk_utils.Variable(varname, marduk_utils.VariableType.STATE, present, next)
    try:
        marduk.add_variable(var)
        marduk.spec_debug_utils._SpecDebugUtils__mc_vars.append(var)
        marduk.spec_debug_utils._SpecDebugUtils__present_mc_var_bdds.append(present)
        marduk.spec_debug_utils._SpecDebugUtils__next_mc_var_bdds.append(next)
        marduk.spec_debug_utils._SpecDebugUtils__present_mc_cube *= var.ps
        marduk.spec_debug_utils._SpecDebugUtils__next_mc_cube *= var.ns

    except mdk.MardukException, arg:
        print arg.message
        raise arg
    marduk.vars_dict[varname] = var

    return var

def getVariableBddByName(marduk, varname, next=False):
    if not next:
        return marduk.vars_dict[varname].ps
    else:
        return marduk.vars_dict[varname].ns

def checkRealizability(filename, marduk = None):
    """Checks whether the property in the .rat file filename is realizable"""
    # This initializes a Marduk object

    if marduk is None:
        marduk = initMarduk(filename)

    # Checks realizability of a specification
    winning_region = wr.WinningRegion(marduk, marduk.specification)
    winning_region.calcWinningRegion()
    marduk.winning_region = winning_region


    ## This resets NuSMV. It is an ugly trick, but it is the only safe way to have Ratsy reset it without changing
    ## its internal code.
    tree = mdom.parse(filename)
    signals = SignalsModel()
    signals.from_xml(tree, tree.documentElement)
    reqs = RequirementsModel()
    reqs.from_xml(tree, tree.documentElement)
    # Create a GameLogicModel object just to call the _reset_nusmv() method on it
    game = GameLogicModel(signals, reqs)
    game.marduk = marduk
    game.utils = SpecDebugUtils(game.marduk)
    game._reset_nusmv()

    return winning_region.isRealizable()

def computeCounterstrategy(specfile, countersfile, marduk=None):
    """Computes a counterstrategy for specfile and saves it in countersfile. Returns True if the counterstrategy was created
    and False if not (because the specification in specfile was realizable)."""

    if marduk is None:
        marduk = initMarduk(specfile)

    tree = mdom.parse(specfile)
    signals = SignalsModel()
    signals.from_xml(tree, tree.documentElement)
    reqs = RequirementsModel()
    reqs.from_xml(tree, tree.documentElement)
    # Create a GameLogicModel object
    game = GameLogicModel(signals, reqs)
    game.marduk = marduk
    game.utils = marduk.spec_debug_utils

    winning_region = wr.WinningRegion(marduk, marduk.specification)
    winning_region.calcWinningRegion()
    marduk.winning_region = winning_region
    if not winning_region.isRealizable():
        game._minimize()
        # Compute counterstrategy
        game._counters()
        game._countertrace()

        # Create counterstrategy graph
        strategy = game.play_engine.strategy
        strategy_initial_state = game.utils.get_env_init_ix_jx()
        onion_rings = game.play_engine.play_history.onion_rings
        trace = game.play_engine.play_history.trace
        # 100 means, that the computation is aborted if 100 states are
        # exceeded in the graph:
        path_finder = PathFinder(game.utils, strategy, onion_rings, trace, 1000)
        # False means that the graph shoule not be deleted after it was written
        # to the file (we need it in the game). True means references to nodes should
        # be deleted
        success = path_finder.write_graphs(countersfile, True)
        counterstrategy_created = True
    else:
        counterstrategy_created = False
        strategy = None
        strategy_initial_state = None

    # Reset NuSMV to make it possible to parse new specifications
    game._reset_nusmv()
    # game.utils contains the cointerstrategy along with other structures needed for its analysis
    # (like the BDD of all the variables, called "cube")
    return counterstrategy_created, strategy, strategy_initial_state

# Utility function for minidom.
def minidom_getRequirementFromName(tree,reqname):
    reqs = tree.getElementsByTagName('requirement')
    for req in reqs:
        if req.getElementsByTagName('name')[0].childNodes[0].data == reqname:
            return req.getElementsByTagName('property')[0].childNodes[0].data
    return None

def getUnrealizableCoreNames(specfile):
    """Computes an unrealizable core for a given specification."""
    """Computes a counterstrategy for specfile and saves it in countersfile. Returns True if the counterstrategy was created
        and False if not (because the specification in specfile was realizable)."""
    # This initializes a Marduk object
    marduk_options = mdk.MardukOptions()
    marduk_options.input_file = specfile
    marduk_options.verbose = 0
    marduk_options.dyn_reorder = True
    marduk_options.reorder1 = True
    marduk_options.reorder2 = True
    marduk = mdk.Marduk(marduk_options, None)

    # This reads an XML spec and creates a variable list for marduk
    marduk.specification = s.Specification(marduk)
    marduk.specification.readSpecification()
    marduk.vars = marduk.specification.create_variable_list()

    tree = mdom.parse(specfile)
    signals = SignalsModel()
    signals.from_xml(tree, tree.documentElement)
    reqs = RequirementsModel()
    reqs.from_xml(tree, tree.documentElement)
    # Create a GameLogicModel object
    game = GameLogicModel(signals, reqs)
    game.marduk = marduk
    game.utils = SpecDebugUtils(game.marduk)

    winning_region = wr.WinningRegion(marduk, marduk.specification)
    winning_region.calcWinningRegion()
    marduk.winning_region = winning_region

    if not winning_region.isRealizable():
        # The names of the guarantees in the unrealizable core
        unreal_core_names = extractGuaranteeNamesFromList(game._minimize(), tree)
    else:
        unreal_core_names = []

    # Reset NuSMV to make it possible to parse new specifications
    game._reset_nusmv()

    return unreal_core_names

def getUnrealizableCore(specfile):
    """Computes an unrealizable core for a given specification."""
    """Computes a counterstrategy for specfile and saves it in countersfile. Returns True if the counterstrategy was created
        and False if not (because the specification in specfile was realizable)."""
    # This initializes a Marduk object
    marduk_options = mdk.MardukOptions()
    marduk_options.input_file = specfile
    marduk_options.verbose = 0
    marduk_options.dyn_reorder = True
    marduk_options.reorder1 = True
    marduk_options.reorder2 = True
    marduk = mdk.Marduk(marduk_options, None)

    # This reads an XML spec and creates a variable list for marduk
    marduk.specification = s.Specification(marduk)
    marduk.specification.readSpecification()
    marduk.vars = marduk.specification.create_variable_list()

    tree = mdom.parse(specfile)
    signals = SignalsModel()
    signals.from_xml(tree, tree.documentElement)
    reqs = RequirementsModel()
    reqs.from_xml(tree, tree.documentElement)
    # Create a GameLogicModel object
    game = GameLogicModel(signals, reqs)
    game.marduk = marduk
    game.utils = SpecDebugUtils(game.marduk)

    winning_region = wr.WinningRegion(marduk, marduk.specification)
    winning_region.calcWinningRegion()
    marduk.winning_region = winning_region

    if not winning_region.isRealizable():
        # The names of the guarantees in the unrealizable core
        unreal_core_names = extractGuaranteeNamesFromList(game._minimize(), tree)
    else:
        unreal_core_names = []
    unreal_core = []
    for guar_name in unreal_core_names:
        unreal_core.append(minidom_getRequirementFromName(tree, guar_name))

    # Reset NuSMV to make it possible to parse new specifications
    game._reset_nusmv()


    return unreal_core

def extractGuaranteeNamesFromList(reqs_list, reqs_tree):
    guaranteesList = []

    # The LTL formula of an assumption unit is in the <requirement> element
    for req in reqs_tree.documentElement.getElementsByTagName("requirement"):
        # The <kind> node contains the requirement type (A or G)
        # The <name> node contains the id of the formula
        # mdom accesses the text of a Node via <Node instance>.firstChild.nodeValue
        req_name = req.getElementsByTagName("name")[0].firstChild.nodeValue.lstrip().rstrip()
        if req.getElementsByTagName("kind")[0].firstChild.nodeValue.lstrip().rstrip() == "G" and req_name in reqs_list:
                guaranteesList.append(req_name)

    return guaranteesList

def resetNusmv(marduk):

    if marduk is not None:
        ## This resets NuSMV. It is an ugly trick, but it is the only safe way to have Ratsy reset it without changing
        ## its internal code.
        signals = SignalsModel()
        reqs = RequirementsModel()
        # Create a GameLogicModel object just to call the _reset_nusmv() method on it
        game = GameLogicModel(signals, reqs)
        game.marduk = marduk
        game.utils = SpecDebugUtils(game.marduk)
        game._reset_nusmv()
        print "NuSMV reset"


def main():
    spectree = readRATFile("../Examples/testAddRequirement.rat")
    addRequirement(spectree,"testAdd","G(hbuslock0)","A","0")
    toggleRequirement(spectree,"testAdd")
    print checkRealizability("../CaseStudies/AMBA02/spec.rat")
    computeCounterstrategy("../CaseStudies/AMBA02/spec.rat","../CaseStudies/AMBA02/counterstrategy")

    spectree_2 = mdom.parse("../Examples/testAddRequirement.rat")
    reqs = spectree_2.getElementsByTagName('requirement')
    print reqs
    print reqs[0].getElementsByTagName('name')[0].childNodes[0].data

if __name__=='__main__':
    main()