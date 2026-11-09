import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'simulator'))
from model import Simulation, validate

class SimulatorTests(unittest.TestCase):
    def test_invalid_maps(self):
        for config in [None,[],{'start':[10,4]},{'start':[True,4]},
                       {'obstacles':[[4,4]]},{'obstacles':[[1,1]],'dust':[[1,1]]},
                       {'direction':4},{'direction':True},{'max_ticks':101},{'max_ticks':0},
                       {'dust':'invalid'},{'obstacles':[[1]]},{'name':''},{'requirements':7}]:
            with self.subTest(config=config), self.assertRaises(ValueError): validate(config)
    def test_center_and_defaults(self):
        config=validate({});self.assertEqual(config['start'],[4,4]);self.assertEqual(config['direction'],0)
        self.assertEqual(config['max_ticks'],100)
    def test_duplicate_normalization(self):
        self.assertEqual(validate({'dust':[[1,1],[1,1]]})['dust'],[[1,1]])
    def test_initial_history_is_not_fake_c_output(self):
        sim=Simulation({});self.assertIsNone(sim.history[0]['controller']);self.assertIsNone(sim.history[0]['sensors'])
    def test_boundaries_and_dust_sensing(self):
        sim=Simulation({'start':[0,0],'dust':[[0,0]]})
        self.assertEqual(sim.sensors(),{'front':1,'left':1,'right':0,'dust':1})
    def test_backward_block_is_environment_effect(self):
        sim=Simulation({'obstacles':[[4,3],[3,4],[5,4],[4,5]]})
        f=sim.step();self.assertEqual(f['controller']['motor'],'BACKWARD')
        self.assertTrue(f['collision']);self.assertEqual(f['position'],[4,4])
    def test_reset_and_export_independence(self):
        sim=Simulation({'dust':[[4,4]]});f=sim.step();self.assertNotIn([4,4],f['dust'])
        export=sim.export();export['history'][0]['position'][0]=99
        self.assertEqual(sim.history[0]['position'],[4,4])
        fresh=Simulation(sim.config);self.assertEqual(fresh.history[0]['dust'],[[4,4]])
        self.assertEqual(fresh.history[0]['tick'],0)
    def test_limit_and_determinism(self):
        config={'max_ticks':3,'dust':[[4,4]]}
        a,b=Simulation(config),Simulation(config)
        for _ in range(3):self.assertEqual(a.step(),b.step())
        with self.assertRaises(ValueError):a.step()
        self.assertEqual(len(a.history),4)

if __name__=='__main__': unittest.main(verbosity=2)
