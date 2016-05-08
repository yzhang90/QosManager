set terminal postscript colour
set output 's1_no_qos.eps'

set grid

set ylabel "Bitrate (kb/s)"
set xlabel "Time (s)"

set xrange [0:500]
set yrange [0:6000]

plot "s1_hc1_1.2.dat" title "Video1 (5M)" with lines lw 5, "s1_hc1_2.2.dat" title "Video2 (5M)" with lines lw 5, "s1_hc2.2.dat" title "VoIP (1.2M)" with lines lw 5


