set terminal png medium size 640,480
set output "feedback_graph.png"
set xlabel "Days"
show xlabel
set ylabel "Mark"
show ylabel
set grid
show grid
plot "feedback_graph_data.txt" index "Aratro" with lines title "Aratro", "feedback_graph_data.txt" index "2 Chef" with lines title "2 Chef", "feedback_graph_data.txt" index "Calabianca" with lines title "Calabianca", "feedback_graph_data.txt" index "Concorde" with lines title "Concorde",
