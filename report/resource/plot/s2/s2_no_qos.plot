set terminal postscript colour
set output 's2_no_qos.eps'

set grid

set ylabel "Bitrate (kb/s)"
set xlabel "Time (s)"

set xrange [0:500]
set yrange [0:6000]

plot "s2_hc1.2.dat" title "Video (5M)" with lines lw 5, "s2_hc3_1.2.dat" title "Game1 (3M)" with lines lw 5, "s2_hc3_2.2.dat" title "Game2 (3M)" with lines lw 5


