#!/usr/bin/env python

import phone_iso3166.e212
import phone_iso3166.e212_names
import io
import os
import sys

def generate(filename):
    def transverse(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                for i in transverse(v, path + str(k)):
                    yield i
        else:
            yield path, node

    filehead = """// Code generated by gen/gen.py DO NOT EDIT.
package $GOPACKAGE

import iradix "github.com/hashicorp/go-immutable-radix"

type Operator struct {
    Country string
    Name string
}

type MncMap map[uint16]Operator
type MccMap map[uint16]MncMap

"""
    filehead = filehead.replace('    ', "\t")
    filehead = filehead.replace('$GOPACKAGE', os.environ['GOPACKAGE'])

    with open(filename, 'w') as out:
        out.write(filehead)
        e212 = """
func getE212() *iradix.Tree {
    r := iradix.New()
    t := r.Txn()
"""
        out.write(e212.replace('    ', "\t"))
        for prefix, country in transverse(phone_iso3166.e212.networks, ''):
            out.write(f"\tt.Insert([]byte(\"{prefix}\"), \"{country}\")\n")
        out.write("\treturn t.Commit()\n")
        out.write("}\n\n")

        out.write("var OperatorMap = MccMap{\n")
        for mcc, mncmap in phone_iso3166.e212_names.operators.items():
            out.write(f"\t{mcc}: MncMap{{\n")
            for mnc, oper in mncmap.items():
                cc, name = oper
                name = name.replace('"', '\\"')
                out.write(f"\t\t{mnc}: {{\"{cc}\", \"{name}\"}},\n")
            out.write(f"\t}},\n")
        out.write("}\n")


if __name__ == "__main__":
    generate(sys.argv[1])
