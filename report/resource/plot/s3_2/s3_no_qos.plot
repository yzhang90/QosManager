set terminal postscript colour
set output 's3_no_qos.eps'

set grid

set ylabel "Bandwidth (kb/s)"
set xlabel "Time (s)"

set xrange [0:500]
set yrange [0:6000]

set key font ",18"

plot "s3_hc1.2.dat" title "Video (5M)" with lines lw 5, "s3_hc2.2.dat" title "VoIP (1.2M)" with lines lw 5, "s3_hc3_1.2.dat" title "Game1 (3M)" with lines lw 5, "s3_hc3_2.2.dat" title "Game2 (3M)" with lines lw 5


