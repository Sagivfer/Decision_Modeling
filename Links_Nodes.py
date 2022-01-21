import Utilities
import numpy as np


class Node:
    def __init__(self, name='', value=0.0, links=None, node_type='c'):
        self.name = name
        self.node_type = node_type
        self.links = [] if links is None else []
        self.value = value
        self.utility = 0
        if self.node_type == 'decision':
            self.decision = -1

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_new_link(self, other, probability):
        if self.node_type == 'c':
            link = Link(node_out=self, node_in=other, probability=probability, link_type='chance')
        else:
            link = Link(node_out=self, node_in=other, link_type='decision')
        self.links.append(link)

    def remove_link(self, node_out):
        for l in self.links:
            if l.node_out is node_out:
                self.links.remove(l)

    def calc_utility(self, person):
        if len(self.links) == 0:
            self.utility = person.utility.U(self.value)
        else:
            if self.node_type == 'c':
                self.utility = Utilities.prospect(person, self)
            if self.node_type == 'd':
                utilities = []
                for link in self.links:
                    link.node_in.calc_utility(person)
                    utilities.append(link.node_in.utility)
                self.utility = max(utilities)
                decision = np.argmax(utilities)
                self.decision = decision
                print(f"Chose {self.links[decision].node_in.name} in {self.name}")
        return self.utility

    def __gt__(self, other):
        return self.utility > other.utility


class Link:
    def __init__(self, node_out=None, node_in=None, probability=0, link_type='chance'):
        self.node_out = node_out
        self.node_in = node_in
        self.link_type = link_type
        if link_type == 'chance':
            self.probability = probability
        else:
            self.probability = 0

    def set_node_in(self, node):
        self.node_in = node

    def get_node_in(self):
        return self.node_in

    def set_node_out(self, node):
        self.node_out = node

    def get_node_out(self):
        return self.node_out

    def set_type(self, link_type):
        self.link_type = link_type

    def get_type(self):
        return self.link_type


def check_probabilities(probabilities):
    if sum(probabilities) != 1:
        raise ValueError('Probabilities must sum to 1')


# Simple prospect.
def create_prospect(name, probabilities, outcomes):
    node = Node(name=name, node_type='c')
    # Representing the outcomes as nodes.
    outcomes_nodes = []
    for i in range(len(probabilities)):
        outcomes_nodes.append(Node(value=outcomes[i]))
        # Connecting the nodes to the main one.
        node.set_new_link(other=outcomes_nodes[i], probability=probabilities[i])
    # Return the starting point.
    return node


# Link multiple nodes easily by giving nodes and probabilities.
def link_nodes(start_node, probabilities, nodes):
    if start_node.node_type == 'c':
        if len(nodes) != len(probabilities):
            raise ValueError('Number of nodes must be equal to number of probabilities given')
        check_probabilities(probabilities)
    else:
        probabilities = [0] * len(nodes)
    for i in range(len(nodes)):
        start_node.set_new_link(nodes[i], probabilities[i])


