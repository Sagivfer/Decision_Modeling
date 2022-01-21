import Links_Nodes as LN
import Utilities


person = Utilities.Person(1, weighting_family='power', c=2)
ps = [0.2, 0.3, 0.5]
D20 = LN.create_prospect('D20', ps, [115, 110, 107.5])
D40 = LN.create_prospect('D40', ps, [55, 230, 227.5])
D50 = LN.create_prospect('D50', ps, [25, 200, 287.5])
Root = LN.Node('Root', node_type='d')
LN.link_nodes(Root, [], [D20, D40, D50])
