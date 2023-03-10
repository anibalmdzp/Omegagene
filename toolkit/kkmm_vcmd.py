#!/usr/bin/python2.7

import sys
import kkkit
import re
import numpy as np
import copy

class VcMDConf():
    def __init__(self):
        self.interval = 0
        #self.n_params = 0
        self.dim = 0
        self.group_names = []
        # group_names[dim] = [name, name]
        # self.group_names[0] is must be empty ("")

        self.n_vs = []
        self.lambda_ranges = []
        # lambda_ranges[dim][vsid] = (min, max)
        self.params = {}
        # params[(vs1, vs2, ...)] = (param1, param2, ...)
        self.qraw_is = {}
        # qraw_is[(vs1, vs2, ..., is1, is2, ...)] = (param1, param2, ...)
        self.qraw_is_state = {}
	# qraw_is_state[(vs1, vs2, ...)][(is1, is2, ...)] = (param1, param2, ...)
        self.qraw = {}        

        self.init_vs = []
        # init_vs[dim] = vsid

        self.seed = -1

        self.surr_states = {}
        ## surr_states[(vs1, vs2, ..., vs_dim)] =
        ##     [(vs1, vs2, ..., vs_dim), (vs1, vs2, ...), ... ]

        self.param_mode = 0
        ## 0 ... raw value in self.params
        ## 1 ... log value in self.params


    def sum_params(self, param_od=0):
        s = 0.0;
        for k,v in self.params.items():
            s += v[param_od]
        return s;
    def read_params(self, fn, chk4gen=True):
        reader = VcMDParamsReader(fn)
        self.interval, self.dim, self.group_names, \
            self.lambda_ranges, self.params, self.n_vs = reader.read(chk4gen)
        self.param_mode = reader.param_mode
        #print("dbg0709b  param_mode ", self.param_mode)
        return 

    def read_qraw_is(self, fn, chk4gen=False):
        ret = VcMDParamsReader(fn).read_qraw_is()
        self.interval = ret[0]
        self.dim = ret[1]
        self.group_names = ret[2]
        self.lambda_ranges = ret[3]
        self.n_vs_l = ret[5]
        self.qraw_is = ret[4]

        
    def read_init(self, fn):
        self.init_vs, self.seed = VcMDInitReader(fn).read(self.dim)
    def add_params(self, conf):
        key = tuple([ 0 for x in range(self.dim)])
        for vs, param in conf.params.items():
            if vs == key: continue
            if not vs in self.params:
                self.params[vs]  = []
                for i, p in enumerate(conf.params[vs]):
                    self.params[vs].append(p)
            else:
                for i, p in enumerate(conf.params[vs]):
                    self.params[vs][i] += p
        return
    def scale_params(self, factor):
        key_def = tuple([ 0 for x in range(self.dim)])
        for vs, param in self.params.items():
            if vs == key_def: continue
            self.params[vs][0] *= factor
        return
    def scale_qraw_is(self, factor):
        key_def = tuple([ 0 for x in range(self.dim)])
        for vs, param in self.qraw_is.items():
            if vs == key_def: continue
            self.qraw_is[vs][0] *= factor
        return
    def param_log(self):
        for vs, param in self.params.items():
            self.params[vs] = np.log(param)
        self.param_mode = 1
        return 

    def param_exp(self):
        for vs, param in self.params.items():
            self.params[vs] = np.exp(param)
        self.param_mode = 0
        return
    def multiply_params(self, conf, factor=1):
        key_def = tuple([ 0 for x in range(self.dim)])
        #print "test"
        #print self.params[key]

        # add default value for VSs in conf
        for vs, param in self.params.items():
            if vs == key_def: continue
            if not vs in conf.params:
                conf.params[vs] = conf.params[key_def]

        conf.normalize_params()
        #for vs, param in conf.params.items():
        #    if vs == key_def: continue
        #    if not vs in self.params:
        #        self.params[vs] = self.params[key_def]
        #self.normalize_params()

        #print("dbg0709", self.param_mode, conf.param_mode)

        for vs, param in conf.params.items():
            if not vs in self.params: continue
            if vs == key_def: continue
            for i, p in enumerate(conf.params[vs]):
                if self.param_mode == 1:
                    if conf.param_mode == 0:
                        p = np.log(p) * factor
                    self.params[vs][i] += p
                else:
                    if conf.param_mode == 1:
                        p = np.exp(p * factor) 
                    else:
                        p = p**factor
                    if self.params[vs][i] > 0:
                        if p > 0:
                            self.params[vs][i] *= p
                        else:
                            self.params[vs][i] *= self.params[vs][i]
                        

            #print self.params[vs]
        return
    def normalize_params(self):
        p_sum = np.zeros(len(list(self.params.values())[0]), dtype=np.float)
        #p_sum = np.zeros(len(self.params.values()[0]), dtype=np.float)
        key_def = tuple([ 0 for x in range(self.dim)])
        for vs, param in self.params.items():
            if vs == key_def: continue
            if self.param_mode == 1:
                param = [ np.exp(p) for p in param ] 
            p_sum += np.array(param)

        print("p_sum")
        print( p_sum)
        p_sum_t = np.zeros(len(list(self.params.values())[0]), dtype=np.float)
        for vs, param in self.params.items():
            if vs == key_def: continue
            #for i, q in enumerate(param):
            if self.param_mode == 0:
                self.params[vs] /= p_sum
            elif self.param_mode == 1:
                self.params[vs] -= np.log(p_sum)
            p_sum_t += param
        print(p_sum_t)
        return
    def pop_zero_vs(self):
        key_def = tuple([ 0 for x in range(self.dim)])
        for vs, param in self.params.items():
            if vs == key_def: continue
            if self.params[vs][0] == 0:
                self.params.pop(vs)
        return

    def add_const(self, const):
        for vs, param in self.params.items():
            for i, p in enumerate(param):
                self.params[vs][i] += const
        return
    def set_default_param(self):
        key_def = tuple([ 0 for x in range(self.dim)])
        #if key_def in self.params: return
        min_param = 1e10
        #print(len(self.params.items()))
        for k, v in self.params.items():
            if k == key_def: continue
            if v[0] < min_param and v[0] > 0:
                min_param = v[0]
        if min_param == 1e10:
            min_param = 1
        self.params[key_def] = [min_param]
        #self.params[key_def].append(min_param)
        # print min_param
        return
    def sum_qraw_is(self, conf):
        for k, v in conf.qraw_is.items():
            if k in self.qraw_is:
                for i, c_v in enumerate(v):
                    if len(self.qraw_is[k]) > i:
                        self.qraw_is[k][i] += c_v
                #print(k,self.qraw_is[k])
            else:
                self.qraw_is[k] = v
        return
    def gen_qraw_is_state(self):
        self.qraw_is_state = {}
        for k, v in self.qraw_is.items():
            state_key = []
            is_key = []
            for i in range(self.dim):
                state_key.append(k[i])
                is_key.append(k[self.dim+i])
            state_key = tuple(state_key)
            is_key = tuple(is_key)
            if not state_key in self.qraw_is_state:
                self.qraw_is_state[state_key] = {}
            self.qraw_is_state[state_key][is_key] = v
        return
    def normalize_qraw(self):
        qraw_sum = 0
        for k, v in self.qraw.items():        
            qraw_sum += v
        for k, v in self.qraw.items():
            self.qraw[k] = v/qraw_sum
        return
    def sum_qraw_is_state(self):
        """
        Summation qraw_is_state values for each state
        and record as self.qraw
        """
        ret = {}
        for k_state, sub_dict in self.qraw_is_state.items():
            qraw = 0.0
            for k_is, val in sub_dict.items():
                qraw += val[0]
            self.qraw[k_state] = qraw
        return
    def symmetrize(self):
        vs_param01 = {}
        vs_num = {}
        vs_vs = {}
        for key, val in self.params.items():
            uvs = list(copy.deepcopy(key))
            uvs.sort()
            uvs = tuple(uvs)
            if not uvs in vs_num:
                vs_num[uvs] = 0
                vs_param01[uvs] = 0.0
                vs_vs[uvs] = []
            vs_num[uvs] += 1
            vs_param01[uvs] += val[0]
            vs_vs[uvs].append(key)
        for uvs, vss in vs_vs.items():
            sym_param01 = vs_param01[uvs]/float(vs_num[uvs])
            for i_vs in vss:
                self.params[i_vs][0] = sym_param01
        return
    def statistics(self):
        buf = []
        key_def = tuple([ 0 for x in range(self.dim)])
        for k, v in self.params.items():
            if k == key_def: continue
            buf.append(v[0])
        param = np.array(buf)
        print("min: " + str(param.min()))
        print("max: " + str(param.max()))
        print("mean: " + str(param.mean()))
        print("sd: " + str(param.std()))
        return
    def is_in_range(self, vs, lmb):
        assert(len(vs)==self.dim and len(lmb)==self.dim)
        flg = True
        for d in range(self.dim):
            if lmb[d] < self.lambda_ranges[d+1][vs[d]][0] or \
               lmb[d] >= self.lambda_ranges[d+1][vs[d]][1]:
                flg=False; break
        return flg
    def get_surrounding_states_sub(self, vs, cur_dim, vs_list):
        #print("vs : ", vs)
        #print("cur_dim : ", cur_dim)
        #print("self.dim : ", self.dim)
        #print("tmp : ", self.lambda_ranges[cur_dim+1])
        if cur_dim >= self.dim: return
        if vs[cur_dim] > 1:
            cur_vs = list(copy.deepcopy(vs))
            cur_vs[cur_dim] -= 1
            vs_list.add(tuple(cur_vs))
            self.get_surrounding_states_sub(cur_vs, cur_dim+1, vs_list)
        if vs[cur_dim] < len(self.lambda_ranges[cur_dim+1])-1:
            cur_vs = list(copy.deepcopy(vs))
            cur_vs[cur_dim] += 1
            vs_list.add(tuple(cur_vs))
            self.get_surrounding_states_sub(cur_vs, cur_dim+1, vs_list)
        cur_vs = copy.deepcopy(vs)
        vs_list.add(tuple(cur_vs))
        self.get_surrounding_states_sub(vs, cur_dim+1, vs_list)
        return
    
    def get_surrounding_states(self, vs):
        if vs in self.surr_states:
            return self.surr_states[vs]
        else:
            vs_list = set()
            self.get_surrounding_states_sub(vs, 0, vs_list)
            self.surr_states[vs] = vs_list
            return vs_list
        return

    def count_overlapping_states(self, vs, lmb):
        surr = self.get_surrounding_states(vs)
        #print("surr ",surr)
        n_ovl = 0
        for c_vs in surr:
            if self.is_in_range(c_vs, lmb):
                n_ovl += 1
        return n_ovl
    def get_states_for_lambda_sub(self, cur_vs, vs_cand):
        cur_dim = len(cur_vs)
        if cur_dim == self.dim:
            self.vs_set.add(tuple(cur_vs))
            return
        for i_vs in vs_cand[cur_dim]:
            new_vs = copy.deepcopy(cur_vs)
            new_vs.append(i_vs)
            self.get_states_for_lambda_sub(new_vs, vs_cand)
        return
    def get_states_for_lambda(self, lmb):
        """
        Enumerating virtual states overlapping with the argument lambda value.
        """
        states = []
        vs_axes = []
        for  i_dim in range(self.dim):
            dim = i_dim + 1
            vs_axes_dim = []
            for i_vs in range(self.n_vs[i_dim]):
                vs = i_vs+1
                if lmb[dim-1] <=  self.lambda_ranges[dim][vs][0]: break
                if lmb[dim-1] >   self.lambda_ranges[dim][vs][1]: continue
                vs_axes_dim.append(vs)
            vs_axes.append(vs_axes_dim)
        self.vs_set = set()
        
        self.get_states_for_lambda_sub([], vs_axes)
        return self.vs_set

class VcMDInitReader(kkkit.FileI):
    def __init__(self, fn):
        super(VcMDInitReader, self).__init__(fn)
        return
    def read(self, in_dim):
        self.open()
        init_vs = [0]
        ## The fist line:  The number of dimension
        dim = int(self.readline_comment().strip())
        ## The initial VS for each dimension, in each line
        for i in range(dim):
            tmp = int(self.readline_comment().strip())
            init_vs.append(tmp)
        # Random Seed
        seed = int(self.readline_comment().strip())
        if not dim == in_dim:
            sys.stderr.write("Inconsistency in the definition of dimensions.\n")
            sys.stderr.write("VcMD paramter file:      " + str(in_dim) + "\n")
            sys.stderr.write("VcMD initial state file: " + str(dim) + "\n")
            sys.exit(1)
        #print "dbg kkmm_vcmd : seed " + str(seed) + "  dim " + str(dim)
        return init_vs, seed

class VcMDParamsWriter(kkkit.FileO):

    def __init__(self, fn):
        super(VcMDParamsWriter, self).__init__(fn)
    def write(self, vc, param_type=0, param_mode=0):
        """
        param_type:
          0 ... VcMDConf.param
          1 ... VcMDConf.qraw_is
        param_mode
          0 ... raw value
          1 ... log value
        """
        self.open()
        self.f.write(str(vc.interval))
        if param_mode  == 1:
            self.f.write(" LOG")
        self.f.write("\n")
        self.f.write(str(vc.dim)+"\n")        
        for d in range(1, vc.dim+1):
            buf = ""
            buf += str(len(vc.lambda_ranges[d])-1)
            for name in vc.group_names[d]:
                buf += " " + name
            self.f.write(buf+"\n")
            for lmbd in vc.lambda_ranges[d][1:]:
                self.f.write(str(lmbd[0]) + " " + str(lmbd[1]) + "\n")
        params = {}
        if param_type==0:
            params = vc.params
        elif param_type==1:
            params = vc.qraw_is
        else:
            stderr.write("Invalid param_type:", param_type)
            
        keys = params.keys()
        #keys.sort()
        for vs in keys:
            prm = params[vs]
            if prm[0] == 0: continue
            # for vs, param in vc.params.items():
            buf = " ".join([str(x) for x in vs]) 
            for x in prm:
                val = x
                if param_mode == 0 and vc.param_mode == 1:
                    val = np.exp(x)
                elif param_mode == 1 and vc.param_mode == 0:
                    val = np.log(x)
                buf += " " + str(val)
            self.f.write(buf+"\n")
        self.f.write("END")
        self.close()

class VcMDParamsReader(kkkit.FileI):
    def __init__(self, fn):
        self.param_mode = 0
        super(VcMDParamsReader, self).__init__(fn)
    def read(self, chk4gen=True):
        interval, dim, group_names, lambda_ranges, ret_params, n_vs_l = self.read_sub()
        params = {}
        for terms in ret_params:
            crd = tuple([int(x) for x in terms[:dim]])
            assert(not crd in params)
            param = [float(x) for x in terms[dim:]]
            try:
                assert(len(param) < 2)
            except:
                sys.stderr.write("WARNING: In the current version, only one parameter for each VS is allowed. The parameters except for the first are ignored.\n")
                sys.stderr.write("\t".join(terms)+"\n")

            if chk4gen:
                try:
                    assert(0 in crd or param[0] > 0)
                except:
                    sys.stderr.write("WARNING: The parameter shoud be larger than zero.\n")
                    sys.stderr.write("\t".join(terms)+"\n")
            params[crd] = param
        return interval, dim, group_names, lambda_ranges, params, n_vs_l
        
    def read_qraw_is(self):
        interval, dim, group_names, lambda_ranges, ret_params, n_vs_l = self.read_sub()
        params = {}
        for terms in ret_params:
            crd = tuple([int(x) for x in terms[:(dim*2)]])
            assert(not crd in params)
            param = [float(x) for x in terms[(dim*2):]]
            params[crd] = param
        return interval, dim, group_names, lambda_ranges, params, n_vs_l        
        
    def read_sub(self, chk4gen=True):
        self.open()
        params = {}

        # The first line: VS transition interval (step)
        terms = self.readline_comment().strip().split()
        interval = int(terms[0])
        self.param_mode = 0 # raw value
        if len(terms) >= 2:
            if terms[1] == "LOG":
                self.param_mode = 1 # raw value                
                print("parameter file: LOG value")
        # The second line: the number of dimensions
        dim = int(self.readline_comment().strip().split()[0])
        lambda_ranges = [(0.0, 0.0)]
        n_states = 1
        group_names = [[""]]
        n_vs_l = []
        ret_params = []
        # Definitions of VS ranges in each dimension
        for i in range(dim):
            cur_dim = i+1
            # [The number of VS] [Group name] [Group name]
            terms = self.readline_comment().strip().split()
            n_vs = int(terms[0])
            n_vs_l.append(n_vs)
            group_names.append([])
            for tm in terms[1:]:
                group_names[-1].append(tm)
            cur_ranges = [(0,0)]
            for j in range(n_vs):
                # [Min lambda] [Max lambda] 
                terms = self.readline_comment().strip().split()
                try:
                    assert(len(terms) == 2)
                    lmin = float(terms[0])
                    lmax = float(terms[1])
                except:
                    sys.stderr.write("Format error in the VS definition.\n")
                    sys.stderr.write("\t".join(terms))
                    sys.stderr.write("The minimum and maximum values of lambda in each VS should be specified in float values.\n")
                    sys.exit(1)
                cur_ranges.append((float(terms[0]), float(terms[1])))

            lambda_ranges.append(cur_ranges)
            #print "dim " + str(cur_dim)
            #print group_names[-1]
            #print n_vs
            #print cur_ranges
            #print "n_states : " + str(n_states)
        while 1:
            line =self.readline_comment()
            if not line or re.match("end", line, re.IGNORECASE):
                break
            terms = line.strip().split()
            ret_params.append(terms)
        return interval, dim, group_names, lambda_ranges, ret_params, n_vs_l
