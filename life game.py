from random import random
from tkinter import *


# 生命游戏的网格舞台
class Stage:
    # 初始化舞台
    # x, y为舞台大小; ini_cell为初始细胞密度，0 < ini_cell < 1
    # cycle表示舞台是否有边界(无边界为True)
    def __init__(self, **input_dic):                    #input_dic{x, y, ini_cell, cycle}
        self.grid = [[random() < input_dic['ini_cell']
                      for i in range(input_dic['y'])]for j in range(input_dic['x'])]
        self.x = input_dic['x']
        self.y = input_dic['y']
        self.cycle_grid = input_dic['cycle']
        self.mutate = input_dic['mutate']

    # 计算下一代细胞
    def reproduce(self):
        # 周围的细胞个数计数
        def cnt(x, y):
            result = 0
            loc = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if (i, j) != (0, 0)]
            if self.cycle_grid:
                for i, j in loc:
                    if self.grid[(x+i) % self.x][(y+j) % self.y]:
                        result += 1
            else:
                for i, j in loc:
                    if 0 <= x+i < self.x and 0 <= y+j < self.y and self.grid[x+i][y+j]:
                        result += 1
            return result

        newgrid = []
        for i in range(self.x):
            newline = []
            for j in range(self.y):
                result = cnt(i, j)
                # 规则: 旁边3细胞则生成, 旁边2细胞维持原状, 否则细胞死亡
                if result == 3:
                    newpx = True
                elif result == 2:
                    newpx = self.grid[i][j]
                else:
                    newpx = False
                newpx = not newpx if random() < self.mutate else newpx
                newline.append(newpx)
            newgrid.append(newline)
        self.grid = newgrid


# UI的滚动条控制栏
class Bar_Frame:
    def __init__(self, root, t):
        self.frame = Frame(root)
        self.frame.pack(padx=5, pady=5, fill=X)
        txt = {'dense': '初始细胞密度：', 'mutate': '突变概率：'}
        Label(self.frame, text=txt[t]).pack(side=LEFT)
        self.num = StringVar(value={'dense': 0.05, 'mutate': 0.00025}[t])
        self.type = t
        self.bar = Scrollbar(self.frame, orient=HORIZONTAL, command=self.cmd)
        self.bar.set({'dense': 0.05, 'mutate': 0.05}[t],
                     {'dense': 0.05, 'mutate': 0.05}[t])
        self.bar.pack(fill=X)
        Label(self.frame, textvariable=self.num).pack(side=LEFT)

    def getnum(self):
        return float(self.num.get())

    def cmd(self, *args):
        if self.type is 'dense':
            if args[0] == 'scroll':
                if args[1] == '1':
                    num = round(min(float(self.num.get()) + 0.1, 0.99), 2)
                else:
                    num = round(max(0.01, float(self.num.get()) - 0.1), 2)
            elif args[0] == 'moveto':
                num = round(float(args[1])*0.98+0.01, 2)
            self.bar.set(num, num)
        else:
            if args[0] == 'scroll':
                if args[1] == '1':
                    loc = min((float(self.num.get())*10)**0.5 + 0.1, 1)
                else:
                    loc = max(0, (float(self.num.get())*10)**0.5 - 0.1)
            elif args[0] == 'moveto':
                loc = float(args[1])
            num = loc**2/10
            prec = 4 if num > 0.01 else 5 if num > 0.001 else 6
            num = round(num, prec)
            self.bar.set(loc, loc)
        self.num.set(num)


# 舞台长宽的输入栏
class Stagedata_Frame:
    def __init__(self, root):
        # 设置舞台长宽的框架
        self.frame = Frame(root)
        self.frame.pack(padx=5, pady=5, fill=X)
        self.data = {}
        self.entry = {}
        param = (('line', '舞台大小： 行：', LEFT, 80), ('col', '列：', LEFT, 80))
        for i in range(2):
            Label(self.frame, text=param[i][1]).pack(side=param[i][2])
            self.data[param[i][0]] = StringVar(value=param[i][3])
            self.entry[param[i][0]] = Entry(self.frame, width=5, textvariable=self.data[param[i][0]],
                                validate='key', validatecommand=(isinstance, int))
            self.entry[param[i][0]].pack(padx=[0, 5], side=param[i][2])
        self.data['gen'] = StringVar(value=200)
        self.entry['gen'] = Entry(self.frame, width=5, textvariable=self.data['gen'],
                                        validate='key', validatecommand=(isinstance, int))
        self.entry['gen'].pack(side=RIGHT)
        Label(self.frame, text='繁衍代数：').pack(padx=[5, 0], side=RIGHT)

    # 获取输入参数
    def getx(self):
        return int(self.data['line'].get())

    def gety(self):
        return int(self.data['col'].get())

    def getgen(self):
        return int(self.data['gen'].get())

    # 控件激活与关闭
    def op_activate(self):
        for item in self.entry.values():
            item['state'] = NORMAL

    def op_disabled(self):
        for item in self.entry.values():
            item['state'] = DISABLED


# 舞台框架和播放控制按钮
class Canvas_Frame:
    def __init__(self, root, framedic):
        self.frame = Frame(root)
        self.frame.pack(padx=5, pady=5)
        # 三个控制按钮
        self.calButton = Button(self.frame, text='开始计算',
                                command=self.cal)
        self.calButton.pack(padx=5, side=LEFT)
        self.framedic = framedic
        self.startButton = Button(self.frame, text='播放', command=self.start)
        self.startButton.pack(padx=5, side=LEFT)
        self.pauseButton = Button(self.frame, text='暂停', command=self.pause)
        self.pauseButton.pack(padx=5)
        self.startButton['state'] = DISABLED
        self.pauseButton['state'] = DISABLED
        self.canvas = Canvas(root, height=0)
        self.canvas.pack(padx=5, pady=5)

    # 一次计算所有代的情况，存到log中
    def cal(self):
        self.framedic['stagedata'].op_disabled()
        self.stage = Stage(x=self.framedic['stagedata'].getx(), y=self.framedic['stagedata'].gety(),
                           ini_cell=self.framedic['dense'].getnum(), cycle=False,
                           mutate=self.framedic['mutate'].getnum())
        self.canvas.config(width=5*self.stage.y+4, height=5*self.stage.x+4)
        self.log = []
        self.pixels = []
        for i in range(self.framedic['stagedata'].getgen()):
            self.log.append(self.stage.grid)
            self.stage.reproduce()
        print('ok')
        for line in range(self.stage.x):
            linelst = []
            for col in range(self.stage.y):
                px = self.canvas.create_rectangle((2+col*5, 2+line*5, col*5+7, line*5+7),
                                             fill='white' if self.log[0][line][col] else 'black',
                                             outline='')
                linelst.append(px)
            self.pixels.append(linelst)
        self.currentGen = 0
        self.framedic['stagedata'].op_activate()
        self.startButton['state'] = NORMAL

    # 按下开始按钮
    def start(self):
        self.startButton['state'] = DISABLED
        self.pauseButton['state'] = NORMAL
        self.newframe()

    def pause(self):
        self.pauseButton['state'] = DISABLED
        self.startButton['state'] = NORMAL

    # 刷新下一帧
    def newframe(self):
        if self.startButton['state'] == NORMAL:
            return
        self.currentGen += 1
        maxgen = len(self.log)
        if self.currentGen < maxgen:
            for line in range(self.stage.x):
                for col in range(self.stage.y):
                    if self.log[self.currentGen][line][col] is not\
                            self.log[(self.currentGen-1) % maxgen][line][col]:
                        self.canvas.itemconfig(self.pixels[line][col],
                                               fill='white' if self.log[self.currentGen][line][col]\
                                                   else 'black')
            self.canvas.after(200, self.newframe)
        else:
            self.currentGen = -1
            self.startButton['state'] = NORMAL
            self.pauseButton['state'] = DISABLED


# 总体UI框架
class UI:
    def __init__(self):
        self.tk = Tk()
        self.tk.title('生命游戏')
        self.tk.geometry('+%d+%d' % ((self.tk.winfo_screenwidth() / 2 - 200),
                         self.tk.winfo_screenheight() / 2 - 300))
        self.tk.wm_minsize(370, 235)
        self.stagedata_frame = Stagedata_Frame(self.tk)
        self.densebar = Bar_Frame(self.tk, 'dense')
        self.mutate = Bar_Frame(self.tk, 'mutate')
        self.canvas = Canvas_Frame(self.tk, {"stagedata": self.stagedata_frame,
                                             'dense': self.densebar, 'mutate': self.mutate})


ui = UI()
ui.tk.mainloop()
