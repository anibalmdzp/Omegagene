#

####################################
ifort -o abc.exe   coef_to_T.f
####################################

  ./abc.exe > data_c_to_T

rm abc.exe

exit
################################################

