# SizeFS

Size-only filesystem for analyzing relative area occupied by various cores in design.

1. Run `dump_hierarchy.tcl` in Synopsys DC on top-level of your project to write out hierarchy to `output.json` file. Examine it and cleanup any warning messages from Synopsys DC.
2. Run `sizefs.py <output.json.gz> <mountpount>` to mount FUSE filesystem
3. Use any disk usage software (`du`, `xdiskusage`, `filelight` etc.) to view to result.

