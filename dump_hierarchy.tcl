proc dump_hierarchy { root } {
    if { [string equal $root ""] } {
        set xroot ""
    } {
        set xroot $root/
    }
    set query "${xroot}*"
    set result {}
    foreach_in_collection c [get_cells $query] {
        set cell [get_object_name $c]
        set base_cell [lindex [split $cell /] end]
        if { [get_attribute $c is_hierarchical] } {
            lappend result [format "\"%s\": %s" ${base_cell} [dump_hierarchy ${cell}]]
        } {
            set area [get_attribute $c area]
            lappend result [format "\"%s\": %s" ${base_cell} ${area}]
        }
    }
    return [format "\{%s\}" [join $result ", "]]
}
redirect -f output.json { dump_hierarchy "" }
