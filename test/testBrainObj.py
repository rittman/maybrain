import unittest

from maybrain import brainObj as mbt
import networkx as nx
import numpy as np

class TestBrainObj(unittest.TestCase):
    """
    Test brainObj class from maybrain
    """
    
    def setUp(self):
        self.a = mbt.brainObj() 
        self.SMALL_FILE = "test/data/3d_grid_adj.txt"
        self.MODIF_FILE = "test/data/3d_grid_adj2.txt"
        self.COORD_FILE = "test/data/3d_grid_coords.txt"

    def test_constructor(self):
        self.assertIsInstance(self.a, mbt.brainObj)
        self.assertIsInstance(self.a.G, nx.Graph)
        self.assertNotIsInstance(self.a.G, nx.DiGraph)
        self.assertFalse(self.a.directed)
        self.assertEqual(self.a.G.number_of_nodes(), 0)
        self.assertEqual(self.a.G.number_of_edges(), 0)
        self.assertEqual(self.a.adjMat, None)

    def test_importAdjFile(self):
        self.assertEqual(self.a.importAdjFile("sdfasdf"), -1)
        self.a.importAdjFile(self.SMALL_FILE)
        self.assertEqual(self.a.adjMat.shape, (4,4))
        self.assertEqual(self.a.adjMat[0][0], 0.802077230054)
        self.assertEqual(self.a.G.number_of_nodes(), 4)
        self.assertEqual(self.a.G.nodes()[0], 0)
        self.assertEqual(len(self.a.G.edges()), 0)
        
        b = mbt.brainObj()
        b.importAdjFile(self.MODIF_FILE, delimiter=",", exclnodes = [2,4])
        ### Confirm general info
        self.assertEqual(b.adjMat.shape, (15,15))
        self.assertEqual(b.G.number_of_nodes(), 13)
        self.assertEqual(b.G.number_of_edges(), 0)
        self.assertEqual(b.adjMat[0][0], 0)
        self.assertEqual(b.adjMat[1][0], 1.541495524150943430e-01)
        self.assertTrue(np.isnan(b.adjMat[6][0]))
        ### Confirm excluded nodes
        self.assertTrue(all(np.isnan(x) for x in b.adjMat[:,2]))
        self.assertTrue(all(np.isnan(x) for x in b.adjMat[:,4]))
        self.assertTrue(all(np.isnan(x) for x in b.adjMat[2,:]))
        self.assertTrue(all(np.isnan(x) for x in b.adjMat[4,:]))
    
    def test_importSpatialInfo(self):
        self.assertEqual(self.a.importSpatialInfo("sdfasdf"), -1)
        self.a.importAdjFile(self.SMALL_FILE)
        self.a.importSpatialInfo(self.COORD_FILE)
       
        attrs = mbt.nx.get_node_attributes(self.a.G, "xyz")
        self.assertEqual(self.a.G.number_of_nodes(), 4)
        self.assertEqual(self.a.G.number_of_edges(), 0)
        self.assertEqual(attrs[0][0], 0)
        self.assertEqual(attrs[0][1], 0)
        self.assertEqual(attrs[0][2], 0)
        self.assertEqual(attrs[3][0], 2.)
        self.assertEqual(attrs[3][1], 2.)
        self.assertEqual(attrs[3][2], 0)
        
        attrs2 = mbt.nx.get_node_attributes(self.a.G, "anatlabel")
        self.assertEqual(attrs2[0], '0')
        self.assertEqual(attrs2[3], '3')
    
    def test_applyThreshold(self):
        self.a.importAdjFile(self.MODIF_FILE, delimiter=",", exclnodes = [2,4])
        self.a.importSpatialInfo(self.COORD_FILE) # making sure this doesn't influence the rest
        self.a.applyThreshold()
        allEdges = self.a.G.number_of_edges()
        #Although there are 3 NAs in the file, just the upper half of the matrix is considered
        degrees = self.a.G.degree()
        self.assertEqual(degrees[0], 11)
        self.assertRaises(KeyError, lambda: degrees[2])
        self.assertRaises(KeyError, lambda: degrees[4])
        self.assertEqual(degrees[5], 12)
        
        acceptedEdges = ((0, 1),(0, 5),(1, 5),(3, 5))
        notAccepted   = ((0,0), (1,1), (2,1), (0,2), (0,3), (0,4), (1,2), (1,3), (1,4))
        self.assertTrue( all(e in     self.a.G.edges() for e in acceptedEdges))
        self.assertTrue( all(e not in self.a.G.edges() for e in notAccepted))
        self.assertEqual(self.a.G.number_of_edges(),76) #(15*15 - 15) /2 - 2 - 27
        
        ### edgePC 
        b = mbt.brainObj()
        b.importAdjFile(self.MODIF_FILE, delimiter=",", exclnodes = [2,4])
        b.applyThreshold(thresholdType="edgePC", value=10.5)
        self.assertEqual(b.G.number_of_edges(), int(0.105*allEdges))
        self.assertTrue((1,12) in b.G.edges())
        b.applyThreshold(thresholdType="edgePC", value=0)
        self.assertEqual(b.G.number_of_edges(), 0) 
        
        ### totalEdges
        b.applyThreshold(thresholdType="totalEdges", value=3)
        self.assertEqual(b.G.number_of_edges(), 3) 
        self.assertTrue((1,12) in b.G.edges())
        b.applyThreshold(thresholdType="totalEdges", value=1000)
        self.assertEqual(b.G.number_of_edges(), 76)
        b.applyThreshold(thresholdType="totalEdges", value=0)
        self.assertEqual(b.G.number_of_edges(), 0) 
        
        ### tVal
        b.applyThreshold(thresholdType="tVal", value=3)
        self.assertTrue( all(e[2]['weight'] >= 3 for e in b.G.edges(data=True)))
        self.assertEqual(b.G.number_of_edges(), 0) 
        b.applyThreshold(thresholdType="tVal", value=6.955292039622642530e-01)
        self.assertTrue( all(e[2]['weight'] >= 6.955292039622642530e-01 for e in b.G.edges(data=True)))
        self.assertEqual(b.G.number_of_edges(), 1) 
        b.applyThreshold(thresholdType="tVal", value=0.5)
        self.assertTrue( all(e[2]['weight'] >= 0.5 for e in b.G.edges(data=True)))
        
        ### directed
        c = mbt.brainObj(directed=True)
        c.importAdjFile(self.MODIF_FILE, delimiter=",")
        c.applyThreshold()
        allEdges = c.G.number_of_edges()
        self.assertEqual(c.G.number_of_edges(), 207) #15*15 - 15 -3NAs
        c.applyThreshold(thresholdType="edgePC", value=10.5)
        self.assertEqual(c.G.number_of_edges(), int(0.105*allEdges))
        c.applyThreshold(thresholdType="totalEdges", value=76)
        self.assertEqual(c.G.number_of_edges(), 76)
        c.applyThreshold(thresholdType="totalEdges", value=10000)
        self.assertEqual(c.G.number_of_edges(), 207)
        c.applyThreshold(thresholdType="tVal", value=0.5)
        self.assertTrue( all(e[2]['weight'] >= 0.5 for e in c.G.edges(data=True)))
        
    
    def test_binarise(self):
        self.a.importAdjFile(self.MODIF_FILE, delimiter=",")
        self.a.applyThreshold()
        self.a.binarise()
        self.assertTrue( all(e[2]['weight'] == 1 for e in self.a.G.edges(data=True)))
        
    def test_localThreshold(self):
        self.a.importAdjFile(self.MODIF_FILE, delimiter=",")
        self.a.applyThreshold()        
        temp = nx.minimum_spanning_tree(self.a.G)        
        
        ### Normal
        self.a.localThresholding()
        self.assertEqual(temp.number_of_edges(), self.a.G.number_of_edges())
        self.assertTrue(nx.is_connected(self.a.G))
        
        ### totalEdges
        # normal totalEdges
        self.a.localThresholding(thresholdType="totalEdges", value = 20)
        self.assertEqual(self.a.G.number_of_edges(), 20)
        self.assertTrue(nx.is_connected(self.a.G))
        # short totalEdges
        self.a.localThresholding(thresholdType="totalEdges", value = 1)
        self.assertEqual(self.a.G.number_of_edges(), temp.number_of_edges())
        self.assertTrue(nx.is_connected(self.a.G))
        # bigger totalEdges
        self.a.localThresholding(thresholdType="totalEdges", value = 500000)
        self.assertTrue(nx.is_connected(self.a.G))
        
        ### edgePC
        self.a.applyThreshold()
        allEdges = self.a.G.number_of_edges()        
        
        self.a.localThresholding(thresholdType="edgePC", value = 100)
        self.assertEqual(self.a.G.number_of_edges(), allEdges)
        self.assertTrue(nx.is_connected(self.a.G))
        
        self.a.localThresholding(thresholdType="edgePC", value = 20)
        self.assertEqual(self.a.G.number_of_edges(), int(0.2*allEdges))
        self.assertTrue(nx.is_connected(self.a.G))

#    def test_spatiallyNearest(self):
        

if __name__ == '__main__':
    unittest.main()