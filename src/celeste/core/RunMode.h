#ifndef __RUN_MODE_H__
#define __RUN_MODE_H__

#include <vector>
#include "CelesteObject.h"
#include "Config.h"
#include "MmSystem.h"
#include "WriteTrr.h"

class RunMode : public CelesteObject {
  private:
  protected:
    Config *cfg;
    int     integrator;
    int     electrostatic;

    int com_motion;
    int print_intvl_crd;
    int print_intvl_vel;
    int print_intvl_log;
    int print_intvl_energy;
    int print_intvl_energyflow;

    std::vector<std::string> fn_o_crd;
    std::string fn_o_log;
    std::string fn_o_energy;
    std::string fn_o_energyflow;

    std::vector<WriteTrr *>   writer_trr;
    WriteRestart writer_restart;

  public:
    MmSystem mmsys;

    RunMode();
    ~RunMode();
    virtual int initial_preprocess();
    virtual int terminal_process();
    virtual int set_config_parameters(Config *in_cfg);
};

#endif
