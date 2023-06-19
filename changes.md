## Version 0.2.0 ##

- Remove `name` parameter on most object, except Job
- Job construct now accepts tables as both iterable or dict.
  Tables will now be stored in a TableSet object.
- Experimental linked protection is possible by using a TableSet.
  Although it seems to work fine, this feature is not documented in the manual.
  Therefore, usage cannot be recommended.
