"""Support code for the ClimRR cross-modal benchmark.

Path resolution, checksums, manifest verification, run records, and the
semantics-neutral column profile. **No climate-variable semantics live in this
package.** A column name is an opaque string here; meaning arrives only through
the tracked data dictionary, cited, in documentation --- never in code.
"""

__all__ = ["paths", "checksums", "manifest", "runrecord", "profile"]
