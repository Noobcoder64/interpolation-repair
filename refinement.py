import experiment_properties as exp
import interpolation
# import alur, varbias
import time
import uuid, re, os, ast
# import ref_utils.ratsy_utils as r
# import model_checking as mc
# from Weakness.src.weakness import computeD1_probe, computeD2_probe, Weakness
import numpy as np
import spectra_utils as spectra
import specification as sp

# from gr1_specification import GR1Specification
from spectra_specification import SpectraSpecification

from typing import List


import functools

def requires_spec(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, 'spec', None) is None:
            raise ValueError(f"spec must be set on {self.__class__.__name__} before calling {func.__name__}")
        return func(self, *args, **kwargs)
    return wrapper

class RefinementNode:

    def __init__(self, gr1_units=None, parent_id=None):
        
        self.id = str(uuid.uuid4())
        self.parent_id = parent_id
        
        self.spec: SpectraSpecification = None
        self.gr1_units = gr1_units or [] # List of all units/conjuncts in this refinement

        self.is_y_sat = None
        self.is_realizable = None
        self.is_satisfiable = None
        self.is_well_separated = None

        self.unreal_core = None
        self.counterstrategy = None
        self.path_length = None
        self.is_looping_path = None

        self.interpolant = None
        self.is_interpolant_state_separable = None
        self.num_state_components = None
        self.num_non_io_separable_state_components = None
        self.is_interpolant_fully_separable = None
        self.num_refs_generated = None

        self.repair_core = None

        self.time_y_sat_check = None
        self.time_realizability_check = None
        self.time_satisfiability_check = None
        self.time_well_separation_check = None
        self.time_unreal_core = None
        self.time_counterstrategy = None
        self.time_interpolation = None
        self.time_generation = None
        self.time_refine = None
        self.time_repair_core = None


    #==========================================================================
    # Methods to deal .spectra files

    def set_spec(self, spec: SpectraSpecification):
        self.spec = spec

    def minimiseSpec(self):
        """Minimizes the spec file by removing all guarantees and adding the unrealizable core"""

        if self.unreal_core is None:
            self.getUnrealizableCore()

        core_spec = SpectraSpecification(
            name=self.spec.name,
            inputs=self.spec.inputs,
            outputs=self.spec.outputs,
            assumptions=self.spec.assumptions,
            guarantees=self.unreal_core,
        )
        # core_spec.to_file(self.spec.file_path)
        self.spec = core_spec
        return core_spec

    #===============================================================================================
    # Methods related to assumptions refinement

    def isYSat(self):
        if self.is_y_sat is not None:
            return self.is_y_sat
        time_y_sat_check_start = time.perf_counter()
        self.is_y_sat = self.spec.is_y_sat()
        self.time_y_sat_check = time.perf_counter() - time_y_sat_check_start
        return self.is_y_sat

    def isSatisfiable(self):
        if self.is_satisfiable is not None:
            return self.is_satisfiable
        time_satisfiability_check_start = time.perf_counter()
        self.is_satisfiable = self.spec.is_satisfiable()
        self.time_satisfiability_check = time.perf_counter() - time_satisfiability_check_start
        return self.is_satisfiable

    def isRealizable(self, timeout=600):
        if self.is_realizable is not None:
            return self.is_realizable
        time_realizability_check_start = time.perf_counter()
        self.is_realizable = self.spec.is_realizable(timeout)
        self.time_realizability_check = time.perf_counter() - time_realizability_check_start
        return self.is_realizable

    def isWellSeparated(self):
        if self.is_well_separated is not None:
            return self.is_well_separated
        time_well_separation_check_start = time.perf_counter()
        self.is_well_separated = self.spec.is_well_separated()
        self.time_well_separation_check = time.perf_counter() - time_well_separation_check_start
        return self.is_well_separated
    
    def getUnrealizableCore(self):
        """Gets an unrealizable core for the current node"""
        if self.unreal_core is not None:
            return self.unreal_core
        
        time_unreal_core_start = time.perf_counter()
        self.unreal_core = self.spec.compute_unrealizable_core()
        self.time_unreal_core = time.perf_counter() - time_unreal_core_start
        return self.unreal_core

    def getCounterstrategy(self, timeout=600):
        """Returns a counterstrategy object"""
        if self.counterstrategy is not None:
            return self.counterstrategy
        
        if self.isRealizable():
            return None

        time_counterstrategy_start = time.perf_counter()
        self.counterstrategy = self.spec.compute_counterstrategy(True, timeout)
        self.time_counterstrategy = time.perf_counter() - time_counterstrategy_start
        self.counterstrategy_num_states = self.counterstrategy.num_states
        return self.counterstrategy

    def generateRefinements(self):
        time_generation_start = time.perf_counter()
        refinements = []
        refinements, metrics = interpolation.generateRefinements(self.getCounterstrategy(), self.spec.assumptions + self.gr1_units, self.getUnrealizableCore(), self.spec.inputs)
        self.time_generation = time.perf_counter() - time_generation_start

        self.num_refs_generated = len(refinements)
        self.interpolant = metrics.get("interpolant", None)
        self.time_interpolation = metrics.get("time_interpolation", None)
        self.is_interpolant_state_separable = metrics.get("is_interpolant_state_separable", None)
        self.num_state_components = metrics.get("num_state_components", None)
        self.num_non_io_separable_state_components = metrics.get("num_non_io_separable_state_components", None)
        self.is_interpolant_fully_separable = metrics.get("is_interpolant_fully_separable", None)

        return refinements

    def generateRefinedNodes(self):
        """Produces a list of Refinement objects based on the selected refinement method"""

        time_refine_start = time.perf_counter()
        
        refinements = []
        candidate_refs = self.generateRefinements()
        candidate_refs = sp.spectra_format(candidate_refs)
        for candidate_ref in candidate_refs:
            # Append the refinement generated by just concatenating the new assumption
            refinements.append(RefinementNode(self.gr1_units + [candidate_ref], self.id))

        self.time_refine = time.perf_counter() - time_refine_start
        
        return refinements

    def getRepairCore(self):
        time_repair_core_start = time.perf_counter()
        asm_core = self.spec.compute_assumptions_core()
        repair_core = set(asm_core) & set(self.gr1_units)
        self.time_repair_core = time.perf_counter() - time_repair_core_start
        self.gr1_units = list(repair_core)
        return self.gr1_units
