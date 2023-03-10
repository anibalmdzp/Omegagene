#!/usr/bin/python2.6

from optparse import OptionParser
import sys
import os
import numpy as np
import re
import kkmm_vcmd
import copy
import kkmmconfig
# from collections import defaultdict

def opt_parse():
    p = OptionParser()
    p.add_option('--i-new-vs', dest='fn_new_vs',
                 help="q_cano file")
    p.add_option('-o', dest='fn_out',
                 help="filename for output")    
    p.add_option('--lambda-log', dest='fn_lambda',
                 default="lambda.out",
                 help="lambda log file")    
    p.add_option('--vs-log', dest='fn_vslog',
                 default="ttp_vcmd.out",
                 help="vcmd log file")    
    p.add_option('--o-cano', dest='fn_o_canonical',
                 help="filename for output")    
    p.add_option('-b','--bin-width', dest='bin_width',
                 type="float",
                 help="bin width for lambda")
    p.add_option('--stages', dest='stages',
                 help="numbers separated with 'i,j'. The range can be specified by 'i-j'")
    p.add_option('--series', dest='series',
                 help="numbers separated with 'i,j'. The range can be specified by 'i-j'")
    p.add_option('--rho-entire', dest='rho_entire',
                 action="store_true",
                 help="")
    p.add_option('--cal-dir', dest='cal_dir',
                 default=".",
                 help="")
    opts, args = p.parse_args()
    print "----------------------------"
    p.print_help()
    print "----------------------------"
    return opts, args

class VcMDData(object):
    def __init__(self, bin_width, fn_qweight, fn_lambda, fn_vslog, path_cal):
        self.bin_width = bin_width

        # self.distrib[bin_id][(vs1,vs2...)] = prob
        self.distrib = {}
        # self.distrib[bin_id] = prob
        self.distrib_nrm = {}
        
        self.sum_prob = 0.0
        self.dim = 0

        self.path_cal = path_cal
        self.fn_lambda = fn_lambda
        self.fn_vslog = fn_vslog
        # self.fn_config = fn_config
        # self.fn_qcano = "vcmd_next.inp"
        self.stages = []
        self.series = []

        ## self.files_lambda[stage][series] = "fn"
        self.files_lambda = {} 
        self.files_vslog = {} 
        self.files_qweight = {}


        return
    def parse_unit(self, term):
        at = re.compile("^(\d+)$")
        at_range = re.compile("^(\d+)\-(\d+)$")
        m1 = at.match(term)
        m2 = at_range.match(term)
        val = []
        if m1:
            val = [int(m1.group())]
        elif m2:
            val = [x for x in range(int(m2.group(1)), int(m2.group(2))+1)]
        return val

    def read_fnlist(self, fn):
        f = open(fn)
        fnlist = []
        for line in f:
            tmp = line.strip().split()[0]
            fnlist.append(tmp)
        f.close()
        return fnlist

    def set_trajectory_files(self, stages_str, series_str):
        self.stages = self.parse_unit(stages_str)
        self.series = self.parse_unit(series_str)
        for st in self.stages:

            fn_qweight = os.path.join(self.path_cal, str(st-1), self.fn_qweight)
            

            #fn_cfg = os.path.join(self.path_cal, str(st), "n"+str(self.series[0]), self.fn_config)
            #cfgr = kkmmconfig.ConfigReader(fn_cfg)
            #cfgr.debug=False
            #cfg = cfgr.read_config()
            #fn_qcano = os.path.join(self.path_cal, str(st), "n"+str(self.series[0]), cfg.get_val("fn-i-vcmd-inp"))

            if not os.path.exists(fn_qweight):
                sys.stderr.write("File not found; qweight for the stage "+str(st)+"\n")
                sys.stderr.write(fn_qweight+"\n")
                continue
            self.files_qweight[st] = fn_qweight
            self.files_lambda[st] = {}
            self.files_vslog[st] = {}
            for se in self.series:
                dir_cal = os.path.join(self.path_cal, str(st), "n"+str(se))
                fn_lambda = os.path.join(dir_cal, self.fn_lambda)
                fn_vslog = os.path.join(dir_cal, self.fn_vslog)
                if not os.path.exists(fn_lambda):
                    sys.stderr.write("File not found; \n")
                    sys.stderr.write(fn_lambda+"\n")
                    continue
                if not os.path.exists(fn_vslog):
                    sys.stderr.write("File not found; \n")
                    sys.stderr.write(fn_vslog+"\n")
                    continue
                self.files_lambda[st][se] = fn_lambda 
                self.files_vslog[st][se] = fn_vslog
        #print self.files_lambda
        return
        
    def read_trj(self, fn_trj, dtype="float"):
        trj = []
        f = open(fn_trj)
        for line in f:
            buf = line.strip().split()            
            term = None
            if dtype=="float":
                term = [float(x) for x in buf]
            elif dtype=="int":
                term = [int(x) for x in buf]
            trj.append(term)
        f.close()
        return trj

    def read_lambda(self, fn_trj):
        trj = []
        f = open(fn_trj)
        f.readline()
        for line in f:
            buf = line.strip().split()            
            term = None
            term = [float(x) for x in buf]
            trj.append(term[1:])
        f.close()
        return trj

    def add_distrib(self, vcconf, trj_lambda, trj_vslog, unweighted=False):
        #for i, vs_l in enumerate(trj_vslog):
        for i, lmb in enumerate(trj_lambda):
            vs = tuple(trj_vslog[i])
            if not vcconf.is_in_range(vs, lmb): continue
            bin_id = tuple([int(x/self.bin_width) for x in lmb])

            if not bin_id in self.distrib:
                self.distrib[bin_id] = {}
                self.distrib_nrm[bin_id] = 0.0
            if not vs in self.distrib[bin_id]:
                self.distrib[bin_id][vs] = 0.0
            w = 1
            if not unweighted: w = vcconf.params[vs][0]
            self.distrib[bin_id][vs] += w
            ## self.sum_prob +=  vcconf.params[vs][0]
        return
    def normalize_distrib(self):
        self.sum_prob = 0
        for bin_id, vs_val in self.distrib.items():
            for vs, val in vs_val.items():
                self.distrib_nrm[bin_id] += val / float(len(vs_val.keys()))
                self.sum_prob += val / float(len(vs_val.keys()))
        for bin_id, val in self.distrib_nrm.items():        
            self.distrib_nrm[bin_id] = val / self.sum_prob
        return

    def calc_canonical(self, unweigthed=False):
        self.distrib = {}
        self.sum_prob = 0.0
        for st, fn_qweight in self.files_qweight.items():
            vcconf = kkmm_vcmd.VcMDConf()
            vcconf.read_params(fn_qweight)
            if self.dim == 0:
                self.dim = vcconf.dim
            if self.dim != vcconf.dim:
                sys.stderr.write("Inconsistency in the VS dimension\n")
                sys.stderr.write(fn_qweight+"\n")
                sys.exit(1)

            for se, fn_lambda in self.files_lambda[st].items():
                print("Stage:"+str(st) + " - Series:" + str(se))
                fn_vslog = self.files_vslog[st][se]
                trj_lambda = self.read_lambda(fn_lambda)
                trj_vslog = self.read_trj(fn_vslog, "int")
                #try:
                #    assert(len(trj_vslog)==len(trj_lambda))
                #except:
                #    sys.stderr.write("Data sizes of vslog and lambda were inconsistent.\n")
                #    sys.stderr.write("Stage: " + str(st) + " Series: " + str(se)+"\n")
                #    sys.exit(1)

                self.add_distrib(vcconf, trj_lambda, trj_vslog,
                                 unweigthed)
        self.normalize_distrib()
        return

    def write_canonical(self, fn_cano):
        f = open(fn_cano, "w")
        #sorted(d.items(), key=lambda x:x[1])
        for bin_id, val in sorted(self.distrib_nrm.items(), key=lambda x:x[0]):
            lmb = [ str((x+0.5)*self.bin_width) for x in bin_id ]
            line = " ".join(lmb)+" "+str(val)+"\n"
            f.write(line)
        f.close()
        return

    def enum_vs(self, buf_vs, cur_vs, all_vs):
        if len(buf_vs) < 1: return all_vs
        for i, b0 in enumerate(buf_vs[0]):
            tmp_buf = copy.deepcopy(buf_vs[1:])
            tmp_cur = copy.deepcopy(cur_vs)
            tmp_cur.append(b0)

            if len(tmp_cur) == self.dim:
                all_vs.append(tuple(tmp_cur))
            else:
                all_vs = self.enum_vs(tmp_buf, tmp_cur, all_vs)
        return all_vs
    def find_vs(self, bin_id, vcnew):
        vs = []
        for i_dim, vs_rg in enumerate(vcnew.lambda_ranges[1:]):
            tmp_vs = []
            for tmp, rg in enumerate(vs_rg[1:]):
                vs_id = tmp+1
                if (bin_id[i_dim]+0.5)*self.bin_width > rg[0] and (bin_id[i_dim]+0.5)*self.bin_width <= rg[1]:
                    tmp_vs.append(vs_id)
            vs.append(tmp_vs)
        all_vs = self.enum_vs(vs, [], [])
        return all_vs
    def set_qweight_to_vs(self, vcnew):
        for bin_id, val in self.distrib_nrm.items():
            vs = self.find_vs(bin_id, vcnew)
            for i_vs in vs:
                if not tuple(i_vs) in vcnew.params:
                    vcnew.params[i_vs] = [0.0]
                vcnew.params[i_vs][0] += self.distrib_nrm[bin_id]/float(len(vs))

        vcnew.normalize_params()
        return vcnew

def _main():
    opts, args = opt_parse()

    vcdat = VcMDData(opts.bin_width, fn_qweight,
                     opts.fn_lambda, opts.fn_vslog,
                     opts.cal_dir)
    vcdat.set_trajectory_files(opts.stages, opts.series)

    if opts.rho_entire:
        vcdat.calc_canonical(True)
    else:
        vcdat.calc_canonical(False)    

    if opts.fn_o_canonical:
        vcdat.write_canonical(opts.fn_o_canonical)
    if opts.fn_out:
        vcnew = kkmm_vcmd.VcMDConf()
        vcnew.read_params(opts.fn_new_vs)
        vcnew = vcdat.set_qweight_to_vs(vcnew)
        kkmm_vcmd.VcMDParamsWriter(opts.fn_out).write(vcnew)

    return

if __name__ == "__main__":
    _main()
