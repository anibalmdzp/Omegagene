#ifndef __CELESTE_OBJECT_H__
#define __CELESTE_OBJECT_H__

#define DBG 1

//#include <pair>

// type of real values

// typedef float real;
typedef double real;

// type of real values for pairwise energy calculation in GPU
typedef float real_pw;

// type of real values for summation of force,energy
typedef double real_fc;

// type of real values for bonding potentials
// typedef float real_bp;
typedef double real_bp;

// type of real values for constraint
typedef double real_cst;

#define MAX_N_NB15OFF 32
#define MAX_N_POSRES_PARAMS 32

#ifdef F_MPI
#include <mpi.h>
#define mpi_real MPI_DOUBLE
// # typedef MPI_FLOAT  mpi_real
// # typedef MPI_DOUBLE mpi_real_pw
#define mpi_real_pw MPI_FLOAT
#endif

// typedef pair<int,int> int_pair;
// typedef pair<int,int> real3d;
#include <string>

class CelesteObject {
  private:
  protected:
  public:
    CelesteObject();
    enum { MAX_N_COM_GROUPS = 32 };

    enum { M_TEST = 0, M_DYNAMICS, M_DUMMY };
    enum { PRCS_SINGLE = 0, PRCS_MPI, PRCS_CUDA, PRCS_MPI_CUDA, PRCS_DUMMY };
    enum { INTGRTR_ZHANG = 0, INTGRTR_LEAPFROG_PRESTO, INTGRTR_VELOCITY_VERLET, 
	   INTGRTR_LANGEVIN,INTGRTR_LANGEVIN_VV, INTGRTR_MC, INTGRTR_DUMMY };
    enum {
        ELCTRST_WOLF             = 0,
        ELCTRST_ZERODIPOLE       = 1,
        ELCTRST_ZEROQUADRUPOLE   = 2,
        ELCTRST_ZEROOCTUPOLE     = 3,
        ELCTRST_ZEROHEXADECAPOLE = 4,
        ELCTRST_DEBYE_HUCKEL     = 5,
        ELCTRST_DUMMY
    };
    enum {
      NONBOND_LJ = 0,
      NONBOND_HPS = 1,
      NONBOND_DYMMY
    };
    enum { THMSTT_NONE = 0, THMSTT_SCALING, THMSTT_HOOVER_EVANS, THMSTT_DUMMY };
    enum { CONST_NONE = 0, CONST_SHAKE, CONST_SHAKE_SETTLE, CONST_DUMMY };
    enum { COM_NONE = 0, COM_CANCEL };
    enum { EXTENDED_NONE = 0, EXTENDED_VMCMD, EXTENDED_VAUS, EXTENDED_VCMD, EXTENDED_DUMMY };
    enum { AUSTYPE_0 = 0, AUSTYPE_1, AUSTYPE_2, AUSTYPE_MASSCENTER, AUSTYPE_MIN,
	   AUSTYPE_CRDXYZ,  AUSTYPE_DUMMY };
    enum { LAMBDAOUT_BIN = 0, LAMBDAOUT_ASC, LAMBDAOUT_DUMMY };
    enum { CRDOUT_GROMACS = 0, CRDOUT_PRESTO, CRDOUT_DUMMY };
    enum { DISTREST_NONE = 0, DISTREST_HARMONIC, DISTREST_DUMMY };
    enum { POSREST_NONE = 0, POSREST_HARMONIC, POSREST_DUMMY };
    enum { POSRESTUNIT_NORMAL = 0, POSRESTUNIT_Z, POSRESTUNIT_MULTIWELL01, POSRESTUNIT_INV_HARMONIC };
    //
    static const int MAX_N_ATOMTYPE;
    //

    static const std::string EXE;
    static const std::string ABOUT_ME;
    static const std::string DESCRIPTION;
    static const int         REAL_BYTE;
    static const real        PI;
    static const int         MAGIC_NUMBER;
    static const std::string LS_VERSION;
    static const real        EPS;
    static const real        EPS3;

    static const real ELEM_CHARGE;  //
    static const real AVOGADRO;     // [mol^-1]
    static const real PERMITTIVITY; // [m^-3 kg^-1 s^4 A^2]

    // charge_coeff ELEM_CHARGE**2 * AVOGADRO / (4 * PI * PERMITTIVITY * 1e-10 * 4.184 * 1e+3)
    // [Angestrome cal mol-1]
    static const real CHARGE_COEFF;
    static const real FORCE_VEL;
    static const real GAS_CONST;

    static const real JOULE_CAL;
    static const real KINETIC_COEFF;
    static const real BOLTZMAN;
    //  static const int MAX_N_NB15OFF;

    template <typename TYPE>
    inline const TYPE &max(const TYPE &a, const TYPE &b) {
        return a < b ? b : a;
    }
    template <typename TYPE>
    inline const TYPE &min(const TYPE &a, const TYPE &b) {
        return a > b ? b : a;
    }
    int cross(const double *a, const double *b, double *ret);
    int cross(const float *a, const float *b, float *ret);

    int error_exit(const std::string msg, const std::string error_code);
};

#endif
