#ifndef __CONFIG_H__
#define __CONFIG_H__

#include "CelesteObject.h"
#include <array>
#include <vector>

struct Config : public CelesteObject {
    int         mode   = M_TEST;
    std::string fn_cfg = "md_i.cfg";
    std::string fn_inp = "md_i.inp";

    int processor     = PRCS_SINGLE;
    int gpu_device_id = -1;

    int  integrator_type        = INTGRTR_LEAPFROG_PRESTO;
    int  constraint_type        = CONST_NONE;
    real constraint_tolerance   = 0.000001;
    int  constraint_max_loops   = 1000;
    int  thermostat_type        = THMSTT_NONE;
    real temperature            = 300.0;
    real temperature_init       = -1.0;
    real berendsen_tau          = 0.0;
    int  heating_steps          = 0;
    real thermo_const_tolerance = 0.000001;
    int  thermo_const_max_loops = 1000;

    real_pw     cutoff = 12.0;
    real_pw     cutoff_buf;
    unsigned long    n_steps             = 1;
    real        time_step           = 0.0005;
    int         electrostatic       = ELCTRST_ZERODIPOLE;
    real        ele_alpha           = 0.0;
    int         com_motion          = COM_NONE;
    int         n_com_cancel_groups = 0;
    int         com_cancel_groups[MAX_N_COM_GROUPS];
    int         n_com_cancel_groups_name = 0;
    std::string com_cancel_groups_name[MAX_N_COM_GROUPS];
    int         n_enhance_groups_name = 0;
    std::string enhance_groups_name[MAX_N_COM_GROUPS];
    int         random_seed       = -1;
    int         extended_ensemble = EXTENDED_NONE;

    std::array<int, 3> box_div = {{1, 1, 1}};

    std::vector<int> print_intvl_crd;
    int print_intvl_vel = 0;
    int print_intvl_log;
    int print_intvl_force = 0;
    int print_intvl_energy;
    int print_intvl_energyflow;
    int print_intvl_extended_lambda;
    int print_intvl_restart = 0;

    std::string fn_o_restart     = "md_o.restart";
    std::vector<std::string> fn_o_crd;
    std::vector<std::string> group_o_crd_name;
    std::string fn_o_log         = "md_o.log";
    std::string fn_o_energy      = "md_o.erg";
    std::string fn_o_vmcmd_log;
    std::string fn_o_extended_lambda;
    std::string fn_o_energyflow          = "md_o.efl";
    std::string fn_o_vcmd_start  = "start_o.virt";
    std::string fn_o_vcmd_qraw   = "vcmd_qraw.dat";  
    std::string fn_o_vcmd_qraw_is   = "vcmd_qraw_is.dat";  
    int vcmd_drift = 0;
    int         begin_count_qraw = 0;
    real        extend_default_q_raw = 1e-5;
    int         format_o_crd             = CRDOUT_PRESTO;
    int         format_o_extended_lambda = LAMBDAOUT_BIN;

    int init_vel_just = 0;
    // 0: initial velocity is 0-dt
    // 1: initial velocity is 0

    real_pw nsgrid_cutoff       = cutoff + 1.0;
    int     nsgrid_update_intvl = 1;
    // real nsgrid_min_width = cutoff * 0.5;
    // real nsgrid_max_n_atoms = 100;

    int         dist_restraint_type   = DISTREST_NONE;
    real        dist_restraint_weight = 0.0;
    int         pos_restraint_type    = POSREST_NONE;
    real        pos_restraint_weight  = 0.0;
    real        enhance_sigma         = 0.2;
    real        enhance_recov_coef    = 50;
    std::string fn_o_aus_restart      = "aus_restart_out.dat";

    int print_intvl_group_com = -1;
    std::string fn_o_group_com = "group_com.dat";

    real        dh_dielectric = 0.0;
    real        dh_ionic_strength = 0.0;
    real        dh_temperature = 0.0;

    int         nonbond       = NONBOND_LJ;
    real         hps_epsiron   = 0.0;

    real        expected_num_density = -1.0;
    // int  aus_type = AUSTYPE_MASSCENTER;

    real        langevin_gamma = 0.0;

    real        testmc_delta_x = 1.0;
    real        testmc_delta_y = -1.0;
    real        testmc_delta_z = -1.0;
    real        testmc_max_pot = 1e99;
    real        testmc_max_r2 = 1e99;

    Config() = default;
    Config(std::vector<std::string> &&arg);
    Config(const std::string &filepath) : Config(extract_args_from_file(filepath)) {}
    Config(int argc, char **argv) : Config(std::vector<std::string>(argv + 1, argv + argc)){};
    std::vector<std::string> extract_args_from_file(const std::string &filepath);
    void set_arguments(std::vector<std::string> &&arg);
};

#endif
