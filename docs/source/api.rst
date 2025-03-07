===
API
===

Input Specification
===================

Input data
----------
.. automodule:: piargus.inputspec
   :members: InputData, MetaData, MicroData, TableData, CodeList
   :show-inheritance:

Hierarchies
-----------
.. automodule:: piargus.inputspec.hierarchy
   :members: Hierarchy, TreeHierarchy, FlatHierarchy, LevelHierarchy, TreeHierarchyNode
   :show-inheritance:

Output Specification
====================

Tables
------
.. automodule:: piargus.outputspec
   :members: Table, Apriori, TreeRecode
   :show-inheritance:

Safety rule
-----------
.. automodule:: piargus
   :members: dominance_rule, percent_rule, frequency_rule, request_rule, zero_rule, missing_rule, weight_rule, manual_rule, p_rule, nk_rule,
   :show-inheritance:

Result
======
.. automodule:: piargus
   :members: ArgusReport, TableResult
   :show-inheritance:

Tau-Argus
=========
.. automodule:: piargus
   :members: TauArgus, BatchWriter, Job, JobSetupError
   :show-inheritance:
