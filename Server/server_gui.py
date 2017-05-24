import tkinter as tk
from queue import Queue
from Server.server import Server

version = 1.0

class Window:
    def __init__(self, master, width=500, height=450):
        self.master = master
        self.frame = tk.Frame(self.master, width=width, height=height)
        self.print_queue = Queue()
        # setting title
        self.master.title("Server v%s" % str(version))
        # setting size
        self.frame.pack(fill="both", expand=False)
        self.frame.grid_propagate(False)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        root.maxsize(width=500, height=450)
        root.minsize(width=500, height=450)

        #button frame

        self.button_frame = tk.Frame(self.frame, width=100, height=50)

        #buttons
        self.start_button = tk.Button(self.button_frame, text="Start Server", command=self.start_server)
        self.end_button = tk.Button(self.button_frame, text="Stop Server", command=self.end_server)
        self.clear_button = tk.Button(self.button_frame, text="Clear Console", command=self.clear_log)

        #textbox
        self.text1 = tk.Text(self.frame)
        self.text1.config(state=tk.DISABLED)

        #scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, command=self.text1.yview)
        self.text1['yscrollcommand'] = self.scrollbar.set

        #gridding things
        self.button_frame.grid(row=1, column=0, sticky="nsew")
        self.start_button.pack(side=tk.LEFT)
        self.end_button.pack(side=tk.LEFT)
        self.clear_button.pack(side=tk.LEFT)
        self.text1.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="nsw")

        self.server_address = ('172.16.0.56', 7777)
        root.after(10, self.log_print)
        root.protocol('WM_DELETE_WINDOW', self.on_destroy)

        self.server = Server(self.print_queue)

    def on_destroy(self):
        root.destroy()
        self.end_server()

    def log_print(self):
        if not self.print_queue.empty():
            message = str(self.print_queue.get())
            self.text1.config(state=tk.NORMAL)
            self.text1.insert(tk.INSERT, message + "\n")
            self.text1.config(state=tk.DISABLED)
        root.after(10, self.log_print)

    def clear_log(self):
        self.text1.config(state=tk.NORMAL)
        self.text1.delete('1.0', tk.END)
        print("Console cleared.")
        self.text1.config(state=tk.DISABLED)

    def start_server(self):
        self.server.start(self.server_address)

    def end_server(self):
        self.server.destroy()

root = tk.Tk()
project = Window(root)
root.mainloop()
