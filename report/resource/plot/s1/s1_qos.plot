set terminal postscript colour
set output 's1_qos.eps'

set grid

set ylabel "Bandwidth (kb/s)"
set xlabel "Time (s)"

set xrange [0:500]
set yrange [0:6000]

set key font ",18"

plot "s1_hc1_1.1.dat" title "Video1 (5M)" with lines lw 5, "s1_hc1_2.1.dat" title "Video2 (5M)" with lines lw 5, "s1_hc2.1.dat" title "VoIP (1.2M)" with lines lw 5


