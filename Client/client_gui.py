import tkinter as tk
from queue import Queue
import client


version = 1.0

class Window:
    def __init__(self, master, width=500, height=450):
        self.master = master
        self.frame = tk.Frame(self.master, width=width, height=height)
        #queues
        self.print_queue = Queue()
        self.message_queue = Queue()
        # setting title
        self.master.title("Client v" + str(version))
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
        self.start_button = tk.Button(self.button_frame, text="Connect", command=self.connect)
        self.end_button = tk.Button(self.button_frame, text="Disconnect", command=self.disconnect)
        self.clear_button = tk.Button(self.button_frame, text="Clear Console", command=self.clear_log)

        #textbox
        self.text1 = tk.Text(self.frame)
        self.text1.config(state=tk.DISABLED)

        #entry
        self.entry = tk.Entry(self.frame)
        self.entry.bind("<Key>", self.key_pressed)

        #scrollbar
        self.scrollbar = tk.Scrollbar(self.frame, command=self.text1.yview)
        self.text1['yscrollcommand'] = self.scrollbar.set

        #gridding things
        self.button_frame.grid(row=2, column=0, sticky="nsew")
        self.start_button.pack(side=tk.LEFT)
        self.end_button.pack(side=tk.LEFT)
        self.clear_button.pack(side=tk.LEFT)
        self.entry.grid(row=1,column=0, sticky="nsew")
        self.text1.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="nsw")

        self.server_address = ('172.16.140.174', 7777)
        self.client = client.Client(self.print_queue, self.message_queue)

        root.after(10, self.log_print)
        root.protocol('WM_DELETE_WINDOW', self.on_destroy)

    def key_pressed(self, event):
        if event.char == '\r':
            text = self.entry.get()
            self.entry.delete(0, tk.END)
            self.message_queue.put(text)
            print(text)

    def on_destroy(self):
        root.destroy()
        self.disconnect()

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
        print("Console cleared...")
        self.text1.config(state=tk.DISABLED)

    def connect(self):
        self.client.start(self.server_address, "Jeff")

    def disconnect(self):
        self.client.leave()

root = tk.Tk()
project = Window(root)
root.mainloop()