'''Test neurom.io.utils'''
import os
import numpy as np
from neurom.io.readers import load_data
from neurom.io import utils
from neurom.core.dataformat import COLS
from neurom.core import tree
from nose import tools as nt


_path = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_path, '../../../test_data')
SWC_PATH = os.path.join(DATA_PATH, 'swc')

FILES = [os.path.join(SWC_PATH, f)
         for f in ['Neuron.swc',
                   'Single_apical_no_soma.swc',
                   'Single_apical.swc',
                   'Single_basal.swc',
                   'Single_axon.swc',
                   'sequential_trunk_off_0_16pt.swc',
                   'sequential_trunk_off_1_16pt.swc',
                   'sequential_trunk_off_42_16pt.swc',
                   'Neuron_no_missing_ids_no_zero_segs.swc']]

SOMA_IDS = [[1, 2, 3],
            [],
            [1, 2, 3],
            [1, 2, 3],
            [1, 2, 3],
            [1, 9],
            [2, 10],
            [43, 51],
            [1, 2, 3]]

INIT_IDS = [[4, 215, 426, 637],
            [],
            [4],
            [4],
            [4],
            [2, 10],
            [3, 11],
            [44, 52],
            [4]]


_path = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_path, '../../../test_data')
SWC_PATH = os.path.join(DATA_PATH, 'swc')

RAW_DATA = [load_data(f) for f in FILES]

def test_get_soma_ids():
    for i, d in enumerate(RAW_DATA):
        nt.ok_(utils.get_soma_ids(d) == SOMA_IDS[i])


def test_get_initial_segment_ids():
    for i, d in enumerate(RAW_DATA):
        nt.ok_(utils.get_initial_segment_ids(d) == INIT_IDS[i])


def _check_trees(trees):
    for t in trees:
        nt.ok_(len(list(tree.iter_leaf(t))) == 11)
        nt.ok_(len(list(tree.iter_forking_point(t))) == 10)
        nt.ok_(len(list(tree.iter_preorder(t))) == 211)
        nt.ok_(len(list(tree.iter_postorder(t))) == 211)
        nt.ok_(len(list(tree.iter_segment(t))) == 210)
        leaves = [l for l in tree.iter_leaf(t)]
        # path length from each leaf to root node.
        branch_order = [21, 31, 41, 51, 61, 71, 81, 91, 101, 111, 111]
        for i, l in enumerate(leaves):
            nt.ok_(len(list(tree.iter_upstream(l))) == branch_order[i])


def test_make_tree():
    rd = RAW_DATA[0]
    seg_ids = utils.get_initial_segment_ids(rd)
    trees = [utils.make_tree(rd, seg_id) for seg_id in seg_ids]
    nt.ok_(len(trees) == len(INIT_IDS[0]))
    _check_trees(trees)


def test_make_tree_postaction():
    def post_action(t):
        t.foo = 'bar'

    rd = RAW_DATA[0]
    seg_ids = utils.get_initial_segment_ids(rd)
    trees = [utils.make_tree(rd, root_id=seg_id, post_action=post_action)
             for seg_id in seg_ids]
    for t in trees:
        nt.ok_(hasattr(t, 'foo') and t.foo == 'bar')


def test_make_neuron():
    rd = RAW_DATA[0]
    nrn = utils.make_neuron(rd)
    nt.ok_(np.all([s[COLS.ID] for s in nrn.soma.iter()] == SOMA_IDS[0]))
    _check_trees(nrn.neurite_trees)


def test_make_neuron_post_tree_action():
    def post_action(t):
        t.bar = 'foo'

    rd = RAW_DATA[0]
    nrn = utils.make_neuron(rd, post_action)
    for t in nrn.neurite_trees:
        nt.ok_(hasattr(t, 'bar') and t.bar == 'foo')