from socket import *
from threading import *
from tkinter import *
from time import sleep

HOST = 'localhost' # hostname
PORT = 7777 # comm port

class Grid(object):
  
    def __init__(self, master, lins, cols, cell_h = 50, cell_w = 50):
        self.master = master
        self.cell_h = cell_h
        self.cell_w = cell_w
        self.maxlins = lins
        self.maxcols = cols
        h = lins * cell_h + 1
        w = cols * cell_w + 1
        self.w = Canvas(master, height = h, width = w)
        self.w.configure(borderwidth=0, highlightthickness=0)
        self.w.pack()

        for i in range(0, h, cell_h):
            self.w.create_line([(i, 0), (i, h)])
        for i in range(0, w, cell_w):
            self.w.create_line([(0, i), (w, i)])

    def draw_circle(self, id, lin, col, color):
        x = int(col) * self.cell_h
        y = int(lin) * self.cell_w
        circle(self.w, id, 'c', x + 10, y + 10, x + self.cell_w - 10, y + self.cell_h - 10, lin, col, color).draw()

    def draw_square(self, id, lin, col, color):
        x = int(col) * self.cell_h
        y = int(lin) * self.cell_w
        square(self.w, id, 's', x + 10, y + 10, x + self.cell_w - 10, y + self.cell_h - 10, lin, col, color).draw()

class Server(Thread):
    def __init__(self, grid):
        Thread.__init__(self)
        self.grid = grid
        self.server = socket()
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.client = self.server.accept()[0]
    
    def busca_id(self, id):

        for i in shapeObject.objectList:
            for j in i:
                if(j != 0):
                    if(j[1] == id):
                        return j

        return None
    
    def busca_shapeecolor(self, shape, color):
        for i in shapeObject.objectList:
            for j in i:
                if(j != 0):
                    if((j[2] == shape) and (j[3] == color)):
                        return j

        return None
    
    def process_cmd(self, cmd):
        
        shapes = ['s', 'c']
        colors = ['black', 'red', 'blue', 'green' ,'cyan' ,'magenta' ,'yellow']

        flag = 0
        result = None
        size = len(cmd)
        command = cmd[0]
        reply = 'Done.\r\n'

        try:

            if size % 2 == 0:
                #instrução com ID

                id = cmd[1]

                print(id)

                if id.isnumeric():
                    print('-t')
                    flag = 1
                    result = self.busca_id(id)
                else:
                    reply = 'ID format not recognized.\r\n'
                
            else:
                #instrução sem ID

                id = -1
                shape = cmd[1]
                color = cmd[2]

                if shape in shapes:

                    if color in colors:
                        flag = 2
                        result = self.busca_shapeecolor(shape, color)
                    else:
                        reply = 'Colour not recognized.\r\n'
                else:
                    reply = 'Shape not recognized\r\n'

            if flag != 0:

                if command == '-':

                    if result != None:
                        self.grid.w.delete(result[0])
                        self.grid.w.delete(result[6])
                        shapeObject.objectList[result[4]][result[5]] = 0
                    else:
                        reply = 'Object not found.\r\n'
                
                else:

                    posX = int(cmd[-2])
                    posY = int(cmd[-1])
                    shape = cmd[-4]
                    color = cmd[-3]

                    if(0 <= posX < self.grid.maxlins) and (0 <= posY < self.grid.maxlins):

                        if shapeObject.objectList[posX][posY] == 0:

                            if command == '+':

                                if(int(id) < 0) or (result == None):

                                    if(shape == 'c'):
                                        self.grid.draw_circle(id, posX, posY, color)
                                    else:
                                        self.grid.draw_square(id, posX, posY, color)
                                        
                                else:
                                    reply = "ID already in use.\r\n"

                            elif command == 'm':

                                if result != None:

                                    if shape == 'c':
                                        self.grid.draw_circle(result[1], posX, posY, result[3])
                                    else:
                                        self.grid.draw_square(result[1], posX, posY, result[3])

                                    self.grid.w.delete(result[0])
                                    self.grid.w.delete(result[6])
                                    shapeObject.objectList[result[4]][result[5]] = 0

                                else:
                                    reply = 'Object not found.\r\n'

                            else:
                                reply = 'Command not recognized.\r\n'
                        
                        else:
                            reply = 'Position not available.\r\n'

                    else:
                        reply = 'Position out of range.\r\n'

        except:
            reply = 'Command format not recognized.\r\n'
        
        return reply

    def run(self):

        while True:

            try:

                text = ' '
                while text[-1] != '\n':
                    text += self.client.recv(1024).decode("utf-8")

                if not text:
                    break

                reply = self.process_cmd(text.split())
                self.client.sendall(bytes(reply, "utf-8"))

            except:
                break

        print('Closing Grid World.\r\n')
        self.grid.master.quit()
        self.client.close()

class shapeObject(object):

    objectList = []

    def __init__(self, canvas, id, shape, x1, y1, lin, col, color = 'black'):
        self.canvas = canvas
        self.id = id
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.shape = shape
        self.object = None
        self.textId = None
        shapeObject.objectList[int(lin)][int(col)] = [self.object, self.id, self.shape, self.color, int(lin), int(col), self.textId]

    @staticmethod
    def fillObjectList(lin, col):

        for i in range(lin):
            shapeObject.objectList.append([])
            for j in range(col):
                shapeObject.objectList[i].append(0)

class circle(shapeObject):

    def __init__(self, canvas, id, shape, x1, y1, x2, y2, lin, col, color = 'black'):
        super().__init__(canvas, id, shape, x1, y1, lin, col, color)
        self.x2 = x2
        self.y2 = y2
        self.lin = lin
        self.col = col

    def draw(self):
        shapeObject.objectList[self.lin][self.col][0] = self.canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill = self.color, outline = '')
        shapeObject.objectList[self.lin][self.col][6] = self.canvas.create_text(self.x1 + 20, self.y1 + 20, text = self.id, fill = 'white', font = ('Arial', 10, 'bold'))

class square(shapeObject):

    def __init__(self, canvas, id, shape, x1, y1, x2, y2, lin, col, color = 'black'):
        super().__init__(canvas, id, shape, x1, y1, lin, col, color)
        self.x2 = x2
        self.y2 = y2
        self.lin = lin
        self.col = col

    def draw(self):
        shapeObject.objectList[self.lin][self.col][0] = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill = self.color, outline = '')
        shapeObject.objectList[self.lin][self.col][6] = self.canvas.create_text(self.x1 + 20, self.y1 + 20, text = self.id, fill = 'white', font = ('Arial', 10, 'bold'))

if __name__ == '__main__':

    root = Tk()
    root.title('Grid World')
    grid = Grid(root, 5, 5, cell_h = 60, cell_w = 60)
    shapeObject.fillObjectList(5, 5)
    app = Server(grid).start()
    root.resizable(0, 0)
    root.mainloop()

