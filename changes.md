## Version 0.3.0 ##

- Refactor Hierarchy.
  The implementation is now backed by anytree.
  Individual nodes can be accessed by `get_node()`.
- Hierarchy now has an attribute `indent`.
- Replace methods `to_dataframe` and `from_dataframe` by `to_rows` and `from_rows`.
- Simple HierarchyCode if the code itself is hierarchical.
- `<TOTCODE>` is now always written to metadata.

## Version 0.2.0 ##

- Add support for recode table (requires TauArgus version >= 4.2.4).
- Make `name` parameter on most objects obsolete, except Job.
- Remove obsolete parameter `safety_rules_holding`.
  Parameter `safety_rule` is very flexible and can be passed a dict.
- Improve the methods of `BatchWriter` to accept both strings and objects.
- Tables can now be passed to Job as both iterable or dict.
  Tables will now be stored in a TableSet object.
- Experimental linked protection is possible when using a TableSet.
  Although it seems to produce output, this feature is not documented in the Tau Argus manual.
  Therefore, usage cannot be recommended (a warning will be shown).
