#!/usr/bin/python2.6

from optparse import OptionParser
import numpy
import sys
import kkpdb
import kkpresto
import kkpresto_shake
import kkpresto_restart
import random

GAS_CONST = 8.31451  ## J/molK
BOLTZMANN_CONST = 1.3806488e-23  ## J/K
AVOGADRO_CONST = 6.0221413e+23 ## mol^-1

JOULE_CALORIE = 4.184

DEBUG = True
##DEBUG = False

### Treatment of units
# In this program, SI unit is used. 
# All values will be converted to SI just after input
# Units for input and output are in consistent with Presto, that is,
#   Angstrom in length,
#   femto sec in time,
#   g/mol in atomic mass
#   kilo calorie in energy

class RigidUnit(object):
    def __init__(self):
        self.total_mass = 0.0
        self.mass = []
        self.atom_ids = []
    def add_atom(self, atom_id, mass):
        self.atom_ids.append(atom_id)
        self.mass.append(mass)
        self.total_mass += mass

def get_options():
    p = OptionParser()
    
    p.add_option('-i', dest='fn_pdb',
                 help="file name for input PDB generated by tplgene")
    p.add_option('--i-tpl', dest='fn_tpl',
                 help="file name for input TPL")
    p.add_option('--i-shk', dest='fn_shk',
                 help="file name for input SHAKE")
    p.add_option('-t', dest='temperature',
                 type="float",
                 help="Initial temperature of the system")
    p.add_option('-o', dest='fn_restart',
                 help="file name for output restart file")
    p.add_option('-s', dest='random_seed',
                 type = "int", default = 0,
                 help="random seed")
    p.add_option('--mol', dest="flg_mol",
                 action="store_true",
                 help="set COM velocity to zero for each molecule")
    p.add_option('--title', dest='title',
                 default="RESTART generated by kktools",
                 help="file name for input PDB generated by tplgene")
    p.add_option('--check', dest="check",
                 action="store_true",
                 help="checking generated restart file")
    p.add_option('--i-restart', dest='fn_check_restart',
                 help="file name for check restart file")

    opts, args = p.parse_args()
    print "----------------------------"
    p.print_help()
    print "----------------------------"
    return opts,args

def average_mass_of_rigid_units(rigid_units):
    total_mass = 0.0
    for unit in rigid_units:
        total_mass += unit.total_mass
    return total_mass / float(len(rigid_units))

def cal_freedom_of_rigid_units(rigid_units):
    freedom = 0
    for unit in rigid_units:
        if len(unit.atom_ids) == 1:
            freedom += 3
        elif len(unit.atom_ids) == 2:
            freedom += 5
        elif len(unit.atom_ids) == 3:
            freedom +=6
        elif len(unit.atom_ids) == 4:
            freedom +=6
    return freedom

def convert_velocity_si_to_ang_fs(vel):
    for i, v in enumerate(vel):
        vel[i] = v * 1.0e-5
    return vel
def convert_velocity_ang_fs_to_si(vel):
    for i, v in enumerate(vel):
        vel[i] = v * 1.0e+5
    return vel
    
def extract_rigid_units_from_atom_ids(target_atom_ids, rigid_units):
    t_rigid_units = []
    for unit in rigid_units:
        if len(set(unit.atom_ids).intersection(target_atom_ids)) > 0:
            t_rigid_units.append(unit)
    return t_rigid_units

def make_rigid_units(model, tpl, shk):
    atom_id_mass = []
    rigid_units = []
    mol_id = 0
    mol_num = 0
    mol_atom_id = 0
    atom_id_head = 0
    processed_atom_id = set()
    if DEBUG:
        print "######### make_rigid_units () #############"
        print "number of atoms: " + str(len(model.atoms))
    tmp_one_atom_units = []

    for atom_id, atom in enumerate(model.atoms):
        mol_atom_id += 1
        if mol_atom_id == len(tpl.mols[mol_id].atoms)+1:
            mol_atom_id = 1
            mol_num += 1
            atom_id_head = atom_id
            if tpl.mols[mol_id].mol_num == mol_num:
                for tmp_unit in tmp_one_atom_units:
                    if not tmp_unit.atom_ids[0] in processed_atom_id:
                        processed_atom_id.add(tmp_unit.atom_ids[0])
                        rigid_units.append(tmp_unit)                    
                mol_num = 0
                mol_id += 1
        mass = tpl.mols[mol_id].atoms[mol_atom_id-1].mass
        atom_id_mass.append(mass)
        if atom_id in processed_atom_id:
            continue

        unit = RigidUnit()
        unit.add_atom(atom_id, mass)

        if shk and mol_id < len(shk) and mol_atom_id in shk[mol_id]:
            for shk_atom_id in shk[mol_id][mol_atom_id].atom_ids:
                #print "mol_id: " + str(mol_id) + " shk_atom_id:" + str(shk_atom_id) + " " + str(len(tpl.mols[mol_id].atoms))
                shk_mass = tpl.mols[mol_id].atoms[shk_atom_id-1].mass
                unit.add_atom(atom_id_head + shk_atom_id - 1, shk_mass)
                processed_atom_id.add(atom_id_head + shk_atom_id - 1)
            processed_atom_id.add(atom_id)        
            rigid_units.append(unit)
        else:
            tmp_one_atom_units.append(unit)
            
    for tmp_unit in tmp_one_atom_units:
        if not tmp_unit.atom_ids[0] in processed_atom_id:
            processed_atom_id.add(tmp_unit.atom_ids[0])
            rigid_units.append(tmp_unit)                    
    if DEBUG:
        print "Number of rigid units: " + str(len(rigid_units))

    return rigid_units, atom_id_mass

def cal_total_moment(rigid_units, unit_vel):
    total_moment = numpy.array([0.0,0.0,0.0])
    total_mass = 0.0
    for i, unit in enumerate(rigid_units):
        vel = unit_vel[i]
        total_mass += unit.total_mass
        mx = unit.total_mass * vel[0]
        my = unit.total_mass * vel[1]
        mz = unit.total_mass * vel[2]
        total_moment += numpy.array([mx,my,mz])
    return total_moment/total_mass

def remove_total_moment(unit_vel, total_moment):
    for vel in unit_vel:
        vel -= total_moment
    return unit_vel

def mb_dist_3d(temprature, mass):
    const = -2.0*GAS_CONST*temprature / mass
    rand1 = random.random()
    rand2 = random.random()
    rand3 = random.random()
    rand4 = random.random()
    rand5 = random.random()
    rand6 = random.random()
    vx = numpy.sqrt(const * numpy.log(rand1))*numpy.cos(2*numpy.pi*rand2)
    vy = numpy.sqrt(const * numpy.log(rand3))*numpy.cos(2*numpy.pi*rand5)
    vz = numpy.sqrt(const * numpy.log(rand5))*numpy.cos(2*numpy.pi*rand6)
    return numpy.array([vx,vy,vz])

def generate_velocities_random(rigid_units, temperature):
    ## unit_vel[] = [numpy.array(x,y,z)]
    unit_vel = []
    sum_vel = numpy.array([0.0,0.0,0.0])
    sum_mass = 0.0
    sum_vel_mass = 0.0
    sum_kinetic = 0.0

    for unit in rigid_units:
        vel_tmp = mb_dist_3d(temperature, unit.total_mass)
        unit_vel.append(vel_tmp)
        sum_mass += unit.total_mass
        sum_vel_mass += unit.total_mass * vel_tmp
        if DEBUG:
            sum_kinetic += (vel_tmp[0]**2 + vel_tmp[1]**2 + vel_tmp[2]**2) * unit.total_mass 
            sum_vel += vel_tmp
    if DEBUG:
        freedom = cal_freedom_of_rigid_units(rigid_units)
        print "###### Generate Random Velocities ######"
        print "Total velocity"
        print sum_vel
        print "Total kinetic momentum"
        print sum_kinetic
        print "Temperature"
        print sum_kinetic / (GAS_CONST * float(freedom))
        print "Total vel_mass"
        print sum_vel_mass
        print "Total vel_mass/mass"
        print sum_vel_mass / sum_mass

    trans = -sum_vel_mass/sum_mass
    if len(rigid_units) > 1:
        for vel in unit_vel:
            vel += trans
        #vel -= sum_vel / float(len(rigid_units))
        
    if DEBUG:
        print "###### Remove Translation Momentum ######"
        freedom = cal_freedom_of_rigid_units(rigid_units)
        sum_vel = numpy.array([0.0,0.0,0.0])
        sum_moment = numpy.array([0.0,0.0,0.0])
        sum_kinetic = 0.0
        for i,vel in enumerate(unit_vel):
            sum_vel += vel
            sum_moment += vel * rigid_units[i].total_mass
            sum_kinetic += (vel[0]**2 + vel[1]**2 + vel[2]**2) \
                * rigid_units[i].total_mass
        print "Total velocity"
        print sum_vel
        print "Total momentum"
        print sum_moment
        print "Temperature"
        print sum_kinetic / (GAS_CONST * float(freedom))

    return unit_vel

def get_atom_id_molname(tpl):
    atom_id_molname =[]
    for mol in tpl.mols:
        for i in range(0, mol.mol_num):
            for at in mol.atoms:
                atom_id_molname.append(mol.mol_name)
    return atom_id_molname

def set_atomid_list_from_mol(mol_names, model, tpl):
    atom_id_molnames = get_atom_id_molname(tpl)
    atomids = set()
    for atom_id, molname in enumerate(atom_id_molnames):
        if molname in mol_names:
            atomids.add(atom_id)
    return atomids

def set_atomid_all(tpl):
    atomids = []
    for mol_id, tpl_mol in tpl.items():
        for atom in tpl_mol.atoms:
            atomids.append(atom.atom_id-1)
    return atomids

def assign_unit_velocities_to_atoms(rigid_units, unit_vel, atom_vel,
                                    temperature):
    if DEBUG:
        print "##### assign_unit_velocities_to_atoms ####"
    mol_atom_ids = set()
    for i, unit in enumerate(rigid_units):
        for atom_id in unit.atom_ids:
            atom_vel[atom_id] = numpy.copy(unit_vel[i])
            mol_atom_ids.add(atom_id)

    sum_kine = 0.0
    sum_moment = numpy.array([0.0,0.0,0.0])
    sum_moment_shk =numpy.array([0.0,0.0,0.0])

    for i, unit in enumerate(rigid_units):
        tmp_mass = 0.0
        for j, atom_id in enumerate(unit.atom_ids):
            sum_kine += (atom_vel[atom_id][0] ** 2 + \
                             atom_vel[atom_id][1] ** 2 + \
                             atom_vel[atom_id][2] ** 2) * \
                             unit.mass[j]
            sum_moment += atom_vel[atom_id] * unit.mass[j]
            tmp_mass += unit.mass[j]

        sum_moment_shk += unit_vel[i] * unit.total_mass

    freedom = cal_freedom_of_rigid_units(rigid_units)

    if DEBUG:
        print "Total moment"
        print str(sum_moment) + ' <= ' + str(sum_moment_shk) 
        print "Total kinetic momentum"
        print sum_kine
        print "Temperature"
        print sum_kine / (GAS_CONST * float(freedom))
        
    nu = temperature * GAS_CONST * float(freedom)
    
    const = numpy.sqrt(nu / sum_kine)
    if len(rigid_units) < 2:
        const = 0.0

    sum_new_kine = 0.0
    for i, unit in enumerate(rigid_units):
        a_vel = unit_vel[i] * const
        for atom_id in unit.atom_ids:
            atom_vel[atom_id] = a_vel

    return atom_vel

def cal_temperature(target_atom_ids, atom_vel, atom_id_mass, freedom):
    total_kine = 0.0
    for atom_id in target_atom_ids:
        total_kine += (atom_vel[atom_id][0]**2.0 +
                       atom_vel[atom_id][1]**2.0 +
                       atom_vel[atom_id][2]**2.0) * atom_id_mass[atom_id]
    ## total_kine [ J/mol ]
    ### [J/mol] = [kg/mol * m^2 / s^2] = [g/mol * A^2 / fs^2] * 1e7 

    temperature = total_kine / (GAS_CONST * float(freedom))

    return temperature

#def scale_velo_target_atoms(target_atom_ids, atom_vel, temperature,
#                            atom_id_mass):
#    gen_temperature = cal_temperature(target_atom_ids, atom_vel, atom_id_mass)
#    ratio = numpy.sqrt(temperature / gen_temperature)
#    for atom_id in target_atom_ids:
#        atom_vel[atom_id] *= ratio
#    return atom_vel

def check_total_trans_moment(target_atom_ids, atom_vel, atom_id_mass, rigid_units):
    freedom = cal_freedom_of_rigid_units(rigid_units)
    gen_temperature = cal_temperature(target_atom_ids, atom_vel, atom_id_mass, freedom)
    if DEBUG:
        print "TEMPERATURE:" + str(gen_temperature)
    tv = numpy.array([0.0, 0.0, 0.0])
    tm = numpy.array([0.0, 0.0, 0.0])
    
    for atom_id in target_atom_ids:
        tv += atom_vel[atom_id] * atom_id_mass[atom_id]
    print tv
    return 0

def genevelo_target_atoms(target_atom_ids, rigid_units,
                          atom_vel,
                          temperature,
                          atom_id_mass):
    unit_vel = generate_velocities_random(rigid_units, temperature)
    ##total_moment = cal_total_moment(rigid_units, unit_vel)
    ##unit_vel = remove_total_moment(unit_vel, total_moment)
    atom_vel = assign_unit_velocities_to_atoms(rigid_units, unit_vel, atom_vel,
                                               temperature)

    if DEBUG:
        print "ASSIGN ATOMS"
        check_total_trans_moment(target_atom_ids, atom_vel, atom_id_mass, rigid_units)

    #atom_vel = scale_velo_target_atoms(target_atom_ids, atom_vel,
    #                                   temperature, atom_id_mass)

    #if DEBUG:
    #    print "AFTER CORR"
    #    check_total_trans_moment(target_atom_ids, atom_id_mass, atom_vel)
    return atom_vel

def generate_velocities(model, tpl, shk,
                        temperature,
                        mol):
    atom_vel = []
    for i in range(len(model.atoms)):
        atom_vel.append(numpy.array([0.0, 0.0, 0.0]))

    rigid_units, atom_id_mass = make_rigid_units(model, tpl, shk)
    average_unit_mass = average_mass_of_rigid_units(rigid_units)
    print "Average mass of rigid units: " + str(average_unit_mass)
        
    if mol:
        mol_names = []
        for tpl_mol in tpl.mols:
        #    if tpl_mol.mol_name != "WAT" and  \
        #            tpl_mol.mol_name != "CIP" and \
        #            tpl_mol.mol_name != "CIM":
            mol_names.append([tpl_mol.mol_name])
        #mol_names.append(["WAT","CIP","CIM"])
        print mol_names
        for mol_name in mol_names:
            print "################################"
            print "### " + " ".join(mol_name)
            print "################################"
            target_atom_ids = set_atomid_list_from_mol(mol_name, model, tpl)
            print "N_atoms: " + str(len(target_atom_ids))
            t_rigid_units = extract_rigid_units_from_atom_ids(target_atom_ids, rigid_units)
            #print target_atom_ids
            print "DEBUG : " + str(len(t_rigid_units))
            atom_vel = genevelo_target_atoms(target_atom_ids,
                                             t_rigid_units, atom_vel,
                                             temperature,
                                             atom_id_mass)
    else:
        target_atom_ids = set(range(0, len(model.atoms)))
        t_rigid_units = extract_rigid_units_from_atom_ids(target_atom_ids, rigid_units)

        atom_vel = genevelo_target_atoms(target_atom_ids,
                                         t_rigid_units, atom_vel,
                                         temperature,
                                         atom_id_mass)
        
    return atom_vel

def set_model_coordinate_to_restart(model):
    crd = []
    for atom in model.atoms:
        crd.append(atom.crd)
    return crd

def get_atom_id_mass(tpl):
    atom_id_mass =[]
    for mol in tpl.mols:
        for i in range(0, mol.mol_num):
            for at in mol.atoms:
                atom_id_mass.append(at.mass)
    return atom_id_mass

def check_restart(fn_restart, model, tpl, shk):
    rest = kkpresto_restart.PrestoRestartReader(fn_restart).read_restart()
    print rest.crd[0]
    print rest.vel[0]
    rest.vel = convert_velocity_ang_fs_to_si(rest.vel)
    rigid_units, atom_id_mass = make_rigid_units(model, tpl, shk)
    target_atom_ids = set(range(0,len(model.atoms)))

    check_total_trans_moment(target_atom_ids, rest.vel, atom_id_mass, rigid_units)
    return 

def _main():
    opts, args = get_options()

    if opts.random_seed: random.seed(opts.random_seed)
    else: random.seed()

    rest = kkpresto_restart.PrestoRestart()

    print "READ PDB: " + opts.fn_pdb
    model = kkpdb.PDBReader(opts.fn_pdb).read_model()
    rest.n_atoms = len(model.atoms)
    rest.crd = set_model_coordinate_to_restart(model)

    print "READ TPL: " + opts.fn_tpl
    tpl = kkpresto.TPLReader(opts.fn_tpl).read_tpl()
    tpl.convert_units_to_si()
    
    ## for debug
    #for mol_id, mol in enumerate(tpl.mols):
    #print 
    ## 

    shk = None
    n_shk = 0
    if opts.fn_shk:
        print "READ SHK: " + opts.fn_shk
        shk = kkpresto_shake.SHKReader(opts.fn_shk).read_shk()

    if opts.fn_restart:
        print "GENERATE VELOCITIES: "
        rest.n_vel = len(model.atoms)
        rest.vel = generate_velocities(model, tpl, shk,
                                       opts.temperature,
                                       opts.flg_mol)

        print "WRITE RESTART: " + opts.fn_restart
        print rest.crd[0]
        print rest.vel[0]    
        rest.vel = convert_velocity_si_to_ang_fs(rest.vel)
        kkpresto_restart.PrestoRestartWriter(opts.fn_restart).write_restart(rest)

        if opts.check:
            print "CHECKING THE RESTART FILE: "
            check_restart(opts.fn_restart, model, tpl, shk)

if __name__ == "__main__":
    _main()
