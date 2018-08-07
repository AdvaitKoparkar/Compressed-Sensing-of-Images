from Tkinter import *
from tkMessageBox import askretrycancel
import ttk
from test_encrypt import *
import socket, errno
from functools import partial

bg_color = 'white'
fg_color = 'green'

class ClientGUI(Frame, Client):
    def __init__(self, master = None):
        Frame.__init__(self, master)
        # self.master.minsize(500, 500)
        self.configure(background = bg_color)
        self.master.configure(background = bg_color)
        self.pack()

        ip_label = Label(self, text="ip", bg = bg_color, fg = fg_color).grid(row = 0, column = 0)
        port_label = Label(self, text='port', bg = bg_color, fg = fg_color).grid(row = 1, column = 0)
        subrate_label = Label(self, text="subrate", bg = bg_color, fg = fg_color).grid(row = 2, column = 0)
        Label(self, text="error", bg = bg_color, fg = fg_color).grid(row = 3, column = 0)
        Label(self, text="quality", bg = bg_color, fg = fg_color).grid(row = 4, column = 0)
        Label(self, text="block size", bg = bg_color, fg = fg_color).grid(row = 5, column = 0)
        Label(self, text="secret key", bg = bg_color, fg = fg_color).grid(row = 6, column = 0)

        self.ip = StringVar()
        self.ip.set('localhost')
        self.port = StringVar()
        self.port.set(1060)
        self.subrate = StringVar()
        self.subrate.set(0.9)
        self.block_size = StringVar()
        self.block_size.set(16)
        self.error = IntVar()
        self.error.set(0)
        self.quality = IntVar()
        self.quality.set(50)
        self.authentication = StringVar()
        self.authentication.set('0123456789ABCDEF')

        self.clientObj = Client()

        Entry(self, textvariable = self.ip).grid(row = 0, column = 1)
        Entry(self, textvariable = self.port).grid(row = 1, column = 1)
        Entry(self, textvariable = self.subrate).grid(row = 2, column = 1)
        # Scale(self, variable = self.error, from_=0, to=100, length=600, orient=HORIZONTAL).grid(row = 3, column = 1)
        Scale(self, variable = self.error, from_=0, to=100, length=600,tickinterval=5, orient=HORIZONTAL, bg = bg_color, fg = fg_color).grid(row = 3, column = 1)
        Scale(self, variable = self.quality, from_=0, to=100, length=600,tickinterval=5, orient=HORIZONTAL, bg = bg_color, fg = fg_color).grid(row = 4, column = 1)
        OptionMenu(self, self.block_size, "8", "16", "32").grid(row = 5, column = 1)
        Entry(self, show='*', textvariable = self.authentication).grid(row = 6, column = 1)

        Button(self, text = "Connect", command = self.connect_to_server, background = fg_color, fg = 'white').grid(row = 7, column = 1)
        Button(self, text = "Quit", command = self.stop, background = 'red', fg = 'white').grid(row = 7, column = 2)

    def connect_to_server(self):
        try:
            try:
                self.clientObj.stop_processes()
                del(self.clientObj)
                self.clientObj = Client()
                self.clientObj.set_values(self.ip.get(), int(self.port.get()), float(self.subrate.get()), int(self.error.get()), int(self.block_size.get()), int(self.quality.get()), str(self.authentication.get()))
                self.clientObj.client()
            except Exception as e:
                self.clientObj = Client()
                self.clientObj.set_values(self.ip.get(), int(self.port.get()), float(self.subrate.get()), int(self.error.get()), int(self.block_size.get()), int(self.quality.get()), str(self.authentication.get()))
                self.clientObj.client()

        except socket.error as serr:
            if serr.errno == errno.ECONNREFUSED:
                askretrycancel(title = "Socket Error", message = serr)

        except Exception as e:
            print(e)

    def stop(self):
        try:
            self.clientObj.stop_processes()
            self.master.destroy()
        except:
            # print(e)
            self.master.destroy()

if __name__ == '__main__':
    clientGui = ClientGUI()
    # while True:
    #     clientGui.update_idletasks()
    #     clientGui.update()
    clientGui.mainloop()
