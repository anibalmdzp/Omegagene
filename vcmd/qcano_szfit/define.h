#ifndef __DEFINE_H__
#define __DEFINE_H__

#include <string>
#include <ctime>
#include <map>
using namespace std;

//About this program.                                                                                                   
#define EXE ""
#define ABOUT_ME ""
#define ABOUT_ME_PUBLIC ""
#define PI 3.14159265

// mode
enum {
  M_TEST=0,
  M_SUBZONEBASED,
  M_DUMMY
};

// file type
enum {
  FT_PARAMS=0,
  FT_QRAW_IS,
  FT_DUMMY
};

enum {
  UNSAMPLE_OMIT=0,
  UNSAMPLE_MIN
};

enum {
  QW_FILE_MODE_RAW=0,
  QW_FILE_MODE_LOG
};
enum {
  DEFQW_MIN=0,
  DEFQW_MIN01
};
#endif
