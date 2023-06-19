## Version 0.2.0 ##

- Add support for recode table (requires TauArgus version >= 4.2.4).
- Make `name` parameter on most objects obsolete, except Job.
- Tables can now be passed to Job as both iterable or dict.
  Tables will now be stored in a TableSet object.
- Experimental linked protection is possible when using a TableSet.
  Although it seems to produce output, this feature is not documented in the Tau Argus manual.
  Therefore, usage cannot be recommended (a warning will be shown).
