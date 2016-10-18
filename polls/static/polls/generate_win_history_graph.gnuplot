set terminal png medium size 640,480
set output "win_history_graph.png"
set xlabel "Days"
show xlabel
set grid
set grid noxtics
show grid
set key off
set yrange [-1:4]
show yrange
set xrange [-1:]
show xrange
set pointsize 2
set title "Win History" font "sans, 14"
show title
set ytics ("2 Chef" 0, "Aratro" 1, "Calabianca" 2, "Concorde" 3, )
plot "win_history_graph_data.txt" with points pointtype 5
