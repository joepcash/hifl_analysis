import tkinter as tk
from tabulate import tabulate
import predict_points

root = tk.Tk()

root.title("HIFL Predictor")
top_frame = tk.Frame(root).grid()
bottom_frame = tk.Frame(root).grid()

t1 = predict_points.predict_points(100, 700, 0.3)
t1.insert(0,['Team', 'Played', 'Points'])

for i in range(len(t1)):
    for j in range(len(t1[i])):
        print(t1[i][j])
        b = tk.Label(top_frame, text = t1[i][j])
        b.grid(row=i, column=j)

close = tk.Button(bottom_frame, text='Close', width = 25, command = root.destroy)
close.grid(columnspan=3)

root.mainloop()