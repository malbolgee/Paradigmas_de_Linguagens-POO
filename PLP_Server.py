# servidor de Figuras
# para testa-lo, use como cliente o telnet
# Ex: telnet localhost 7777
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

    def draw_circle(self, id, lin, col, cor):
        x = int(col) * self.cell_h
        y = int(lin) * self.cell_w
        circle(self.w, id, 'c', x + 10, y + 10, x + self.cell_w - 10, y + self.cell_h - 10, lin, col, cor).draw()

    def draw_square(self, id, lin, col, cor):
        x = int(col) * self.cell_h
        y = int(lin) * self.cell_w
        square(self.w, id, 's', x + 10, y + 10, x + self.cell_w - 10, y + self.cell_h - 10, lin, col, cor).draw()

class Server(Thread):
    def __init__(self, grid):
        Thread.__init__(self)
        self.grid = grid
        self.server = socket()
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.client = self.server.accept()[0]
    
    def busca_id(self, id):
        for i in range(self.grid.maxlins):
            for j in range(self.grid.maxlins):
                if(shapeObject.objectList[i][j] != 0):
                    if(shapeObject.objectList[i][j][1] == id):
                        return shapeObject.objectList[i][j]

        return None
    
    def busca_formaecor(self, forma, cor):
        for i in range(self.grid.maxlins):
            for j in range(self.grid.maxlins):
                temp = shapeObject.objectList[i][j]
                if(temp != 0):
                    if((temp[2] == forma) and (temp[3] == cor)):
                        return temp

        return None
    
    def process_cmd(self, cmd):

        cores = ['black', 'red', 'blue', 'green' ,'cyan' ,'magenta' ,'yellow']
        formas = ['s', 'c']

        reply = 'Done.\r\n'

        comando = cmd[0]

        if(comando == '-'):
            if(cmd[1].isalpha()):
                forma = cmd[1]
                cor = cmd[2]

                if(cor in cores):
                    if(forma in formas):
                        resultado = self.busca_formaecor(cmd[1], cmd[2])

                    else:
                        reply = 'Shape not recognized.\r\n'
                else:
                    reply = 'Colour not recognized.\r\n'
                
            else:
                resultado = self.busca_id(cmd[1])

            if(resultado != None):
                self.grid.w.delete(resultado[0])
                shapeObject.objectList[resultado[4]][resultado[5]] = 0

            else:
                reply = 'Object not found.\r\n'
        
        else:
            posX = int(cmd[-2])
            posY = int(cmd[-1])

            if((0 <= posX < self.grid.maxlins) and (0 <= posY < self.grid.maxlins)):
                if(shapeObject.objectList[posX][posY] == 0):
                    if(comando == '+'):
                        if(cmd[1].isalpha()):
                            id = -1
                        else:
                            id = cmd[1]

                        if((int(id) < 0) or (self.busca_id(id) == None)):
                            forma = cmd[-4]
                            cor = cmd[-3]

                            if(cor in cores):
                                if(forma == 'c'):
                                    self.grid.draw_circle(id, posX, posY, cor)
                                elif(forma == 's'):
                                    print(id, posX, posY, cor)
                                    self.grid.draw_square(id, posX, posY, cor)
                                else:
                                    reply = 'Shape not recognized.\r\n'

                            else:
                                reply = 'Colour not recognized.\r\n'
                                
                        else:
                            reply = "ID already in use.\r\n"

                    elif(comando == 'm'):
                        if(cmd[1].isalpha()):
                            forma = cmd[1]
                            cor = cmd[2]

                            if(cor in cores):
                                if(forma in formas):
                                    resultado = self.busca_formaecor(cmd[1], cmd[2])
                                    
                                else:
                                    reply = 'Shape not recognized.\r\n'
                            else:
                                reply = 'Colour not recognized.\r\n'
                            
                        else:
                            resultado = self.busca_id(cmd[1])

                        if(resultado != None):
                            if(resultado[2] == 's'):
                                self.grid.draw_square(resultado[1], posX, posY, resultado[3])
                            else:
                                self.grid.draw_circle(resultado[1], posX, posY, resultado[3])

                            self.grid.w.delete(resultado[0])
                            shapeObject.objectList[resultado[4]][resultado[5]] = 0

                        else:
                            reply = 'Object not found.\r\n'

                    else:
                        reply = 'Command not recognized.\r\n'
                
                else:
                    reply = 'Position not available.\r\n'
            else:
                reply = 'Position out of range.\r\n'

        return reply

    def run(self):
        while True:
            # try:
            text = ' '
            while(text[-1] != '\n'):
                text += self.client.recv(1024).decode("utf-8")
                print(text)

            if not text:
                break

            # self.client.sendall(bytes('\r\n', 'utf-8'))
            reply = self.process_cmd(text.split())
            self.client.sendall(bytes(reply, "utf-8"))
            # except:
               # break

        self.grid.master.quit()
        self.client.close()

class shapeObject(object):

    objectList = []

    def __init__(self, canvas, id, shape, x1, y1, lin, col, color = 'black'):
        print(self, id, shape, x1, x1, lin, col, color)
        self.canvas = canvas
        self.id = id
        self.x1 = x1
        self.y1 = y1
        self.color = color
        self.shape = shape
        self.objeto = None

        shapeObject.objectList[int(lin)][int(col)] = [self.objeto, self.id, self.shape, self.color, int(lin), int(col)]

    def draw(self):
        pass

    @staticmethod
    def fillObjectList(lin, col):
        for i in range(lin):
            shapeObject.objectList.append([])
            for j in range(col):
                shapeObject.objectList[i].append(0)

    # @staticmethod
    # def showObjectList(lin, col):

    #     for i in range(lin):
    #         for j in range(col):
    #             print(shapeObject.objectList[i][j], end = '')

    #         print()

class circle(shapeObject):

    def __init__(self, canvas, id, shape, x1, y1, x2, y2, lin, col, color = 'black'):
        super().__init__(canvas, id, shape, x1, y1, lin, col, color)
        self.x2 = x2
        self.y2 = y2
        self.lin = lin
        self.col = col

    def draw(self):
        shapeObject.objectList[self.lin][self.col][0] = self.canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill = self.color, outline = '')

class square(shapeObject):

    def __init__(self, canvas, id, shape, x1, y1, x2, y2, lin, col, color = 'black'):
        super().__init__(canvas, id, shape, x1, y1, lin, col, color)
        self.x2 = x2
        self.y2 = y2
        self.lin = lin
        self.col = col

    def draw(self):
        shapeObject.objectList[self.lin][self.col][0] = self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill = self.color, outline = '')

if __name__ == '__main__':
    root = Tk()
    root.title('Grid World')
    shapeObject.fillObjectList(5, 5)
    grid = Grid(root, 5, 5, cell_h = 60, cell_w = 60)
    app = Server(grid).start()
    root.resizable(0, 0)
    root.mainloop()

