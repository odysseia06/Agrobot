import tkinter as tk

class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Server")

        self.text = tk.Text(master)
        self.text.pack(expand=True, fill="both")

        self.entry = tk.Entry(master)
        self.entry.pack(expand=True, fill="x")
    
        self.frame = tk.Frame(master)
        self.frame.pack()

    def buttons(self, name, function):
        button = tk.Button(master=self.frame, text=name)
        button.pack(side="left")
        button.configure(command=function)

def main():
    root = tk.Tk()
    my_gui = ServerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()