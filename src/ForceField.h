#ifndef __FORCE_FIELD_H__
#define __FORCE_FIELD_H__

#include <cmath>
#include "ForceFieldObject.h"
#include "ZeroMultipoleSum.h"

class ForceField : public ForceFieldObject{
 private:
  
 protected:
  //  MmSystem* mmsys;
  real gmul[11];
  
 public:
  ZeroMultipoleSum* ele;
  ForceField();
  ~ForceField();
  virtual int set_config_parameters(const Config* cfg);
  virtual int initial_preprocess(const PBC* in_pbc);
  
  int calc_bond(real_pw& ene, real_pw work[],
		const real* crd1, const real* crd2,
		const real& param_e, const real& param_r0);
  int calc_angle(real_pw& ene, real_pw work1[], real_pw work2[],
		 const real* crd1, const real* crd2, const real* crd3,
		 const real& param_e, const real& param_theta0);
  int calc_torsion(real_pw& ene,
		   real_pw work1[], real_pw work2[], real_pw work3[],
		   const real* crd1, const real* crd2,
		   const real* crd3, const real* crd4,
		   const real& param_ene,
		   const real& param_overlaps,
		   const real& param_symmetry,
		   const real& param_phase);
  int calc_14pair(real_pw& ene_vdw, real_pw& ene_ele,
		  real_fc work[],
		  const real* crd1, const real* crd4,
		  const real& lj_6term,
		  const real& lj_12term,
		  const real& charge1,
		  const real& charge4,
		  const real& param_coeff_vdw,
		  const real& param_coeff_ele);
  int calc_pairwise(real_pw& ene_vdw, real_pw& ene_ele,
		    real_fc work[],
		    const real* crd1, const real* crd2,
		    const real& param_6term,
		    const real& param_12term,
		    const real& charge1,
		    const real& charge2);
  int calc_zms_excess(real_pw& ene, real_pw work[],
		      const real* crd1, const real* crd2,
		      const real& charge1,
		      const real& charge2);
  
  int cal_self_energy(const int& n_atoms,
		      const int& n_excess,
		      const int**& excess_pairs,
		      
		      /*const int& n_bonds,
		      const int**& bond_atomid_pairs,
		      const int& n_angles,
		      const int**& angle_atomid_triads,
		      const int& n_torsions,
		      const int**& torsion_atomid_quads,
		      const int*& torsion_nb14,*/
		      const real_pw*& charge,
		      real*& energy_self,
		      real& energy_self_sum);
};
 
#endif
 
