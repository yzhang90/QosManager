set terminal postscript colour
set output 's1_loss.eps'

set grid

set ylabel "Lost/Total Datagrams (%)"
set xlabel "Time (s)"

set xrange [0:500]
set yrange [0:100]

plot "s1_hc2.1.loss.dat" title "With QoS" with lines lw 5, "s1_hc2.2.loss.dat" title "Without QoS" with lines lw 5


