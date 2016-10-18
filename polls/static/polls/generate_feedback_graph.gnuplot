set terminal png medium size 640,480
set output "feedback_graph.png"
set xlabel "Days"
show xlabel
set ylabel "Mark"
show ylabel
set grid
show grid
set key left top
show key
set title "Feedback Mark" font "sans, 14"
show title
plot "feedback_graph_data.txt" index "Aratro" with lines title "Aratro" linewidth 3, "feedback_graph_data.txt" index "2 Chef" with lines title "2 Chef" linewidth 3, "feedback_graph_data.txt" index "Calabianca" with lines title "Calabianca" linewidth 3, "feedback_graph_data.txt" index "Concorde" with lines title "Concorde" linewidth 3,
