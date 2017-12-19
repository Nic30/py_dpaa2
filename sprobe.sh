./ls-main ls-addni -n
./ls-main ls-addsw

bridge fdb add 00:00:00:00:00:01 dev sw0p0
bridge fdb add 00:00:00:00:00:02 dev sw0p1
bridge fdb add 00:00:00:00:00:03 dev sw0p2
bridge fdb add 00:00:00:00:00:04 dev sw0p3
