set terminal png medium size 640,480
set output "win_graph.png"
set ylabel "Wins"
show ylabel
set grid
set grid noxtics
show grid
set yrange [0:9]
show yrange
set key off
set boxwidth 1.5 relative
set style fill pattern 2
set title "Wins" font "sans, 14"
show title
set xtics ("2 Chef" 0, "Aratro" 1, "Calabianca" 2, "Concorde" 3, )
plot "win_graph_data.txt" with histogram
