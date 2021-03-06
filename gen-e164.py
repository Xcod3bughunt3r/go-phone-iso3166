#!/usr/bin/env python

import phone_iso3166.e164
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

    head = """// Code generated by gen/gen.py DO NOT EDIT.
// https://blog.golang.org/generate
package $GOPACKAGE

import iradix "github.com/hashicorp/go-immutable-radix"

func getE164() *iradix.Tree {
    r := iradix.New()
    t := r.Txn()
"""
    head = head.replace('    ', "\t")
    head = head.replace('$GOPACKAGE', os.environ['GOPACKAGE'])

    with open(filename, 'w') as out:
        out.write(head)
        for prefix, country in transverse(phone_iso3166.e164.mapping, ''):
            out.write(f"\tt.Insert([]byte(\"{prefix}\"), \"{country}\")\n")
        out.write("\treturn t.Commit()\n")
        out.write("}\n")


if __name__ == "__main__":
    generate(sys.argv[1])
