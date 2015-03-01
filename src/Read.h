#ifndef __READ_H__
#define __READ_H__

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <list>
#include <set>
#include <cstdlib>
#include <cstring>
using namespace std;
#include "CelesteObject.h"
#include "MmSystem.h"
#include "PBC.h"
#include "Constraint.h"

class Read : private CelesteObject {
 private:
  string filename;
  bool op;
  bool conv_endian;

  int size_box;
  int size_crd;
  int size_vel;
  int size_topol;
  int size_constraint;
 public:
  ifstream ifs;
  Read(string inFn);
  string getFn(){return filename;};
  bool is_open(){return op;};
  int open();
  int close();
  vector<string> load_config();
  vector<int> load_integers();
  vector<string> load_strings();
  bool is_conv_endian(){return conv_endian;};
  void set_conv_endian_true(){conv_endian=true;};
  void set_conv_endian_false(){conv_endian=false;};
  template <typename TYPE> int read_bin_values(TYPE *recept, int len);

  int load_launch_set(MmSystem& mmsys);
  int load_ls_header(MmSystem& mmsys);
  int load_ls_box(MmSystem& mmsys);
  int load_ls_crd(MmSystem& mmsys);
  int load_ls_vel(MmSystem& mmsys);
  int load_ls_tpl(MmSystem& mmsys);
  int load_ls_constraint(Constraint* cst);
  //int load_ls_pcluster(MmSystem& mmsys);
};

inline int reverse_endian(int value){
  int v = value;
  //memcpy(&v, &value, sizeof(v));
  v = (int)((v & 0x00FF00FF) << 8 | (v & 0xFF00FF00) >> 8);
  v = (int)((v & 0x0000FFFF) << 16 | (v & 0xFFFF0000) >> 16);  
  //memcpy(&value, &v, sizeof(value));
  return v;
}

inline float reverse_endian(float value){
  int v;
  memcpy(&v, &value, sizeof(v));
  v = ((v & 0x00FF00FF) << 8 | (v & 0xFF00FF00) >> 8);
  v = ((v & 0x0000FFFF) << 16 | (v & 0xFFFF0000) >> 16);  
  return float(v);
}
inline double reverse_endian(double value){
  unsigned char v[8];
  unsigned char v2[8];
  memcpy(&v, &value, sizeof(v));
  for(int i=0; i < sizeof(v); i++){
    memcpy(&v2[7-i],&v[i], sizeof(v[i]));
  }
  //v = ((v&0x00FF00FF00FF00FF) << 8 | (v & 0xFF00FF00FF00FF00) >> 8);
  //v = ((v & 0x0000FFFF0000FFFF) << 16 | (v & 0xFFFF0000FFFF0000) >> 16);  
  //v = ((v & 0x00000000FFFFFFFF) << 32 | (v & 0xFFFFFFFF00000000) >> 32);  
  double ret;
  memcpy(&ret, v2, sizeof(v2));
  return ret;
}
  

#endif
