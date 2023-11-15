#!/bin/false
# -*- coding: utf-8 -*-
import json
import sys
from typing import Any

import pydot


def find(obj, find_key):
    """
    Takes a list and a set.  Returns a list of all matching objects.

    Uses find_inner to recursively traverse the data structure, finding objects
    with keyed by find_key.
    """

    all_matches = [find_inner(item, find_key) for item in obj]
    final = [item for sublist in all_matches for item in sublist]

    return final


def find_inner(obj, find_key) -> list:
    """
    Recursively search through the data structure to find objects
    keyed by find_key.
    """
    results = []

    if not hasattr(obj, "__iter__"):
        # not a sequence type - return nothing
        # this excludes strings
        return results

    if isinstance(obj, dict):
        # a dict - check each key
        for key, prop in obj.items():
            if key == find_key:
                results.extend(prop)
            elif isinstance(prop, dict):
                results.extend(find_inner(prop, find_key))
    elif isinstance(obj, list):
        # a list / tuple - check each item
        for i in obj:
            results.extend(find_inner(i, find_key))

    return results


def make_node_name(function_name: str, state_label: str):
    node_name = f"{function_name}: {state_label}"
    return node_name


def find_edges(states, relname: str) -> str:
    """
    Use find() to recursively find objects at keys matching
    relname, yielding a node name for every result.
    """
    try:
        deps = find(states, relname)
        for dep in deps:
            if isinstance(dep, dict):
                for state_module, dep_name in dep.items():
                    state_module, _, _ = state_module.partition(".")
                    yield f"{state_module}: {dep_name}"
            else:
                yield dep
    except AttributeError as e:
        sys.stderr.write("Bad state: {0}\n".format(str(states)))
        raise e


class Graph(object):
    def __init__(self, input):
        state_obj = json.load(input)
        self.graph = pydot.Dot("states", graph_type="digraph")

        rules: dict[str, dict[str, str | bool]] = {
            "require": {"color": "blue"},
            "require_in": {"color": "blue", "reverse": True},
            "require_any": {"color": "blue", "style": "dashed"},
            "watch": {"color": "red"},
            "watch_in": {"color": "red", "reverse": True},
            "watch_any": {"color": "red"},
            "prereq": {"color": "purple"},
            "prereq_in": {"color": "purple", "reverse": True},
            "use": {"color": "orange"},
            "use_in": {"color": "orange", "reverse": True},
            "onchanges": {"color": "green"},
            "onchanges_in": {"color": "green", "reverse": True},
            "onchanges_any": {"color": "green"},
            "onfail": {"color": "yellow"},
            "onfail_in": {"color": "yellow", "reverse": True},
            "onfail_any": {"color": "yellow"},
        }

        if len(state_obj.keys()) > 1:
            raise Exception(
                "Unsupported: graph for multiple minions: {}".format(
                    ",".join(state_obj)
                )
            )

        minion_obj: dict[str, dict[str, str | list[str | dict[str | Any]]]] = list(
            state_obj.values()
        )[0]

        self.nodes: dict[str, pydot.Node] = {}
        sls = ""

        # sort to prioritiize dunders
        for state_id, props in sorted(minion_obj.items()):
            # Add a node for each state type embedded in this state
            # keys starting with underscores are not candidates

            if state_id == "__extend__":
                # TODO - merge these into the main states and remove them
                sys.stderr.write(
                    "Removing __extend__ states:\n{0}\n".format(str(props))
                )
                continue

            for state_module, function_args in props.items():
                if state_module == "__sls__":
                    sls = f"{state_module[2:-2]}: {function_args}"
                    continue
                elif (
                    len(state_module) > 2
                    and state_module[:2] == "__"
                    and state_module[-2:] == "__"
                ):
                    continue

                state_module, _, function_name = state_module.partition(".")

                for arg in function_args:
                    if isinstance(arg, dict) and arg.get("name"):
                        state_name = arg["name"]
                        break
                else:
                    state_name = state_id

                node_name = make_node_name(state_module, state_id)
                node = pydot.Node(state_id, label=node_name)
                # gather nodes by name and ID, w/ and w/o module
                self.nodes[sls] = node
                self.nodes[f"{state_module}: {state_id}"] = node
                self.nodes[f"{state_module}: {state_name}"] = node
                self.nodes[state_id] = node
                self.nodes[state_name] = node
                self.graph.add_node(node)

        for state_id, props in minion_obj.items():
            # Add a node for each state type embedded in this state
            # keys starting with underscores are not candidates

            if state_id == "__extend__":
                # TODO - merge these into the main states and remove them
                sys.stderr.write(
                    "Removing __extend__ states:\n{0}\n".format(str(props))
                )
                continue

            for state_module, function_args in props.items():
                # ignore dunder data here
                if (
                    len(state_module) > 2
                    and state_module[:2] == "__"
                    and state_module[-2:] == "__"
                ):
                    continue

                state_module, _, function_name = state_module.partition(".")

                for arg in function_args:
                    if isinstance(arg, dict) and arg.get("name"):
                        state_name = arg["name"]
                        break
                else:
                    state_name = state_id

                for relname, ruleset in rules.items():
                    for relname in find_edges(function_args, relname):
                        try:
                            relnode = self.nodes[relname]
                            if "style" not in ruleset or ruleset["style"] is None:
                                ruleset["style"] = ""
                            if "reverse" in ruleset and ruleset["reverse"]:
                                self.graph.add_edge(
                                    pydot.Edge(
                                        state_id,
                                        relnode,
                                        style=ruleset["style"],
                                        color=ruleset["color"],
                                    )
                                )
                            else:
                                self.graph.add_edge(
                                    pydot.Edge(
                                        relnode,
                                        state_id,
                                        style=ruleset["style"],
                                        color=ruleset["color"],
                                    )
                                )
                        except Exception as e:
                            pass

    def render(self, fmt):
        if fmt == "dot":
            return self.graph.to_string()
        else:
            pass
