#ifndef __COM_MOTION_H__
#define __COM_MOTION_H__

#include "CelesteObject.h"
#include "PBC.h"
using namespace std;

class COMMotion : public CelesteObject{
 private:
  int n_groups;
  int* group_ids;
  int* n_atoms_in_groups;
  int** groups;
  real* mass;
  real* mass_inv_groups;
 protected:
 public:
  COMMotion();
  ~COMMotion();
  int set_groups(const int in_n_groups,
		 int* in_group_ids,
		 int* in_n_atoms_in_groups,
		 int** in_groups, real* in_mass_inv_groups,
		 real* in_mass);
  int cancel_translation(int* atomids_rev,
			 real* vel_next);
};

#endif
