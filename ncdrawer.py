import matplotlib
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.colorchooser import *
from netCDF4 import Dataset 
import math
config = {
    "font.family": 'serif', # 衬线字体
    "font.size": 12, # 相当于小四大小
    "font.serif": ['SimSun'], # 宋体
    "mathtext.fontset": 'stix', # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False # 处理负号，即-号
}
plt.rcParams.update(config)

class ncdraw():
    def __init__(self,master):
        self.root=master
        self.root.title("绘图")
        self.fig,self.ax=plt.subplots()
        self.posx_top=400
        self.posy_top=250
        self.root_xsize=int(self.root.winfo_screenwidth()/2)
        self.root_ysize=int(self.root.winfo_screenheight()*3/4)
        self.posx_right=self.posx_top+self.root_xsize
        self.colorbar_axes=None
        self.config={
            "data":"",
            "show_data":"",
            "lons":0,
            "lats":0,
            "var3d":[0],
            "var4d":[0],
            "cmp":["Blues","Blues_r","BrBG","BrBG_r","BuGn","BuGn_r","BuPu","BuPu_r","CMRmap","GnBu","GnBu_r","Greys","OrRd","Oranges","Spectral","jet","rainbow","afmhot","autumn"],
            "cmp_current":"rainbow",
            "z_ind":1,
            "t_ind":1,
            "t_max":0,
            "z_max":0,
            "x_max":0,
            "y_max":0,
            "varmin":0,
            "varmax":0,
        }
        self.draw_fig={
            "xsize":30
        }
        self.show_info=[]
        self.root.geometry("{}x{}+{}+{}".format(self.root_xsize,self.root_ysize,self.posx_top,self.posy_top))
        self.layout()
    def layout(self):
        frame1=ttk.LabelFrame(self.root,width=400,height=600)
        self.canvs = FigureCanvasTkAgg(self.fig, frame1)
        self.canvs.get_tk_widget().pack(side=TOP,fill=X,pady=(1,2))
        #self.menu = ttk.Menu(self.root, tearoff=0)
        #self.menu.add_command(label="打开文件",command=self.openfile)
        #self.root.bind("<Button-3>",self.show_menu)
        frame1.pack(side=TOP,fill=X)
        menubar = ttk.Menu(self.root)
        filemenu = ttk.Menu(menubar, tearoff=False)
        filemenu.add_command(label="打开",command=self.openfile)
        filemenu.add_command(label="输出",command=self.savepic)
        menubar.add_cascade(label="文件", menu=filemenu)
        self.root.config(menu=menubar)
        frame_setting=ttk.Frame(self.root,width=400,height=100)
        frame2=ttk.Frame(frame_setting,width=400,height=100)
        ttk.Label(frame2,text="3DVar",bootstyle="info").grid(row=0,column=0,padx=20,pady=10)
        self.var3d=ttk.StringVar()
        self.type_3d=ttk.Combobox(
            master=frame2,
            values=self.config["var3d"],
            textvariable=self.var3d,
            width=7,
            postcommand=lambda :self.update_3dlist(self.config["var3d"])
        )
        self.type_3d.current(0)
        self.type_3d.bind('<<ComboboxSelected>>',self.update_show3ddata)
        self.type_3d.grid(row=0,column=1)
        ttk.Label(frame2,text="4DVar",bootstyle="info").grid(row=0,column=2,padx=20,pady=20)
        self.var4d=ttk.StringVar()
        self.type_4d=ttk.Combobox(
            master=frame2,
            values=self.config["var4d"],
            textvariable=self.var4d,
            width=7,
            postcommand=lambda :self.update_4dlist(self.config["var4d"])
        )
        self.type_4d.current(0)
        self.type_4d.bind('<<ComboboxSelected>>',self.update_show4ddata)
        self.type_4d.grid(row=0,column=3)
        ttk.Label(frame2,text="Cmp",bootstyle="info").grid(row=0,column=4,padx=20,pady=20)
        self.cmp=ttk.StringVar()
        self.cmp_cb=ttk.Combobox(
            master=frame2,
            values=self.config["cmp"],
            textvariable=self.cmp,
            width=7,
        )
        self.cmp_cb.current(0)
        self.cmp_cb.bind('<<ComboboxSelected>>',self.update_cmp)
        self.cmp_cb.grid(row=0,column=5)

        ttk.Label(frame2,text="Time",bootstyle="info").grid(row=0,column=6,padx=20,pady=20)
        self.tbut=ttk.Button(frame2,text=self.config["t_ind"],command=self.Timeup)
        self.tbut.bind("<Button-3>",self.Timedown)
        self.tbut.grid(row=0,column=7,ipadx=10)

        ttk.Label(frame2,text="Z",bootstyle="info").grid(row=0,column=8,padx=20,pady=20)
        self.zbut=ttk.Button(frame2,text=self.config["z_ind"],command=self.Zup)
        self.zbut.bind("<Button-3>",self.Zdown)
        self.zbut.grid(row=0,column=9,ipadx=10)

        ttk.Label(frame2,text="varmin",bootstyle="info").grid(row=1,column=0)
        self.vi=ttk.Entry(frame2,width=9)
        self.vi.grid(row=1,column=1)
        self.vi.bind("<Return>",lambda a:self.change_varmin(self.vi.get()))

        ttk.Label(frame2,text="varmax",bootstyle="info").grid(row=1,column=2)
        self.vm=ttk.Entry(frame2,width=9)
        self.vm.grid(row=1,column=3)
        self.vm.bind("<Return>",lambda a:self.change_varmax(self.vm.get()))

        reset_but=ttk.Button(frame2,text="RESET",command=self.reset)
        reset_but.grid(row=1,column=4)
        frame2.pack()
        frame_setting.pack(side=TOP,fill=X)
    def savepic(self):
        fname = tk.filedialog.asksaveasfilename(title=u'保存文件', filetypes=[("PNG", ".png"),("JPG", ".jpg"),("SVG",".svg")])
        plt.savefig("{}".format(fname))
    def reset(self):
        try:
            self.config["varmin"]= self.show_info.min()
            self.config["varmax"]= self.show_info.max()
        except:
            pass
        self.vi.delete(0,END)
        self.vm.delete(0,END)
        self.vi.insert(0,round(self.config["varmin"],3))
        self.vm.insert(0,round(self.config["varmax"],3))
        self.draw()
    def change_varmin(self,var):
        try:
            self.config["varmin"]= float(var)
        except:
            pass
        self.draw()
    def change_varmax(self,var):
        try:
            self.config["varmax"]= float(var)
        except:
            pass
        self.draw()
    def Timeup(self):
        #print(self.config["t_max"])
        if self.config["t_ind"]<self.config["t_max"]:
            self.config["t_ind"]=self.config["t_ind"]+1
        self.tbut["text"]=self.config["t_ind"]
        z_ind=self.config["z_ind"]-1
        t_ind=self.config["t_ind"]-1
        try:
            self.show_info=self.config["show_data"][t_ind,z_ind,:,:]
            self.config["varmin"]= self.show_info.min()
            self.config["varmax"]= self.show_info.max()
        except:
            pass
        self.draw()
    def Timedown(self,e):
        if self.config["t_ind"]>2:
            self.config["t_ind"]=self.config["t_ind"]-1
            self.tbut["text"]=self.config["t_ind"]
            z_ind=self.config["z_ind"]-1
            t_ind=self.config["t_ind"]-1
            try:
                self.show_info=self.config["show_data"][t_ind,z_ind,:,:]
                self.config["varmin"]= self.show_info.min()
                self.config["varmax"]= self.show_info.max()
            except:
                pass
        else:
            self.tbut["text"]=1
        self.draw()
    def Zup(self):
        #print(self.config["z_max"])
        if self.config["z_ind"]<self.config["z_max"]:
            self.config["z_ind"]=self.config["z_ind"]+1
        self.zbut["text"]=self.config["z_ind"]
        z_ind=self.config["z_ind"]-1
        t_ind=self.config["t_ind"]-1
        try:
            self.show_info=self.config["show_data"][t_ind,z_ind,:,:]
            self.config["varmin"]= self.show_info.min()
            self.config["varmax"]= self.show_info.max()
        except:
            pass
        self.draw()
    def Zdown(self,e):
        if self.config["z_ind"]>2:
            self.config["z_ind"]=self.config["z_ind"]-1
            self.zbut["text"]=self.config["z_ind"]
            z_ind=self.config["z_ind"]-1
            t_ind=self.config["t_ind"]-1
            try:
                self.show_info=self.config["show_data"][t_ind,z_ind,:,:]
                self.config["varmin"]= self.show_info.min()
                self.config["varmax"]= self.show_info.max()
            except:
                pass
        else:
            self.zbut["text"]=1
        self.draw()
    def update_cmp(self,e):
        self.config["cmp_current"]=self.cmp.get()
        self.draw()
    def update_3dlist(self,lists):
        self.type_3d["values"]=lists
    def update_4dlist(self,lists):
        self.type_4d["values"]=lists
    def update_show3ddata(self,e):
        try:
            self.config["show_data"]=self.config["data"].variables[self.var3d.get()][:]
            self.config["varmin"]=self.config["show_data"].min()
            self.config["varmax"]=self.config["show_data"].max()
            self.config["z_max"]=1
            self.zbut["text"]=1
            self.config["z_ind"]=1
            self.show_info=self.config["show_data"][0,:,:]
            self.config["varmin"]= self.show_info.min()
            self.config["varmax"]= self.show_info.max()
            self.draw()
        except:
            pass
    def update_show4ddata(self,e):
        #print(self.var4d.get())
        try:
            self.config["show_data"]=self.config["data"].variables[self.var4d.get()][:]
            self.config["varmin"]=self.config["show_data"].min()
            self.config["varmax"]=self.config["show_data"].max()
            #print(self.config["varmin"],self.config["varmax"])
            self.config["z_max"]=self.config["show_data"].shape[1]
            z_ind=self.config["z_ind"]-1
            t_ind=self.config["t_ind"]-1
            self.show_info=self.config["show_data"][t_ind,z_ind,:,:]
            self.config["varmin"]= self.show_info.min()
            self.config["varmax"]= self.show_info.max()
            self.draw()
        except:
            pass
    def show_menu(self,event):
        self.menu.post(event.x_root, event.y_root)
    def openfile(self):
        file=tk.filedialog.askopenfilename()
        self.config["data"] = Dataset(file) 
        #print(self.config["data"].variables.keys())
        self.config["var3d"]=[]
        self.config["var4d"]=[]
        for i in list(self.config["data"].variables.keys()):
            if len(self.config["data"].variables[i][:].shape)==3:
                self.config["var3d"].append(i)
            if len(self.config["data"].variables[i][:].shape)==4:
                self.config["var4d"].append(i)
        #print(self.config["var3d"])

        self.Change_data()
        self.draw()
    def Change_data(self):
        self.config["show_data"] =  self.config["data"].variables['U'][:]
        self.config["lons"] = self.config["data"].variables['XLONG'][:]
        self.config["lats"] = self.config["data"].variables['XLAT'][:]
        self.config["z_max"] = self.config["show_data"].shape[1]
        self.config["t_max"] = self.config["show_data"].shape[0]
        lons_range=self.config["lons"].max()-self.config["lons"].min()
        lats_range=self.config["lats"].max()-self.config["lats"].min()
        self.ysize=lats_range*self.draw_fig["xsize"]/lons_range
        self.config["z_ind"]=1
        self.config["t_ind"]=1
        self.tbut["text"]=self.config["t_ind"]
        self.zbut["text"]=self.config["z_ind"]
        self.show_info=self.config["show_data"][0,0,:,:]
        self.config["varmin"]= self.show_info.min()
        self.config["varmax"]= self.show_info.max()
    def num2lon(self,n):
        k=(self.draw_fig["xsize"]-0)/(self.config["lons"].max()-self.config["lons"].min())
        b=0-k*self.config["lons"].min()
        return k*n+b
    def num2lat(self,n):
        k=(self.ysize-0)/(self.config["lats"].max()-self.config["lats"].min())
        b=0-k*self.config["lats"].min()
        return k*n+b
    def draw(self):
        self.ax.clear()
        try:
            #self.ax.set_title("云图显示")
            x2=math.floor(self.config["lons"].max())
            y2=math.floor(self.config["lats"].max())
            x1=math.ceil(self.config["lons"].min())
            y1=math.ceil(self.config["lats"].min())
            xlab=[i for i in range(x1,x2+1)]
            ylab=[i for i in range(y1,y2+1)]
            xlabs=["{}°E".format(i) for i in xlab]
            ylabs=["{}°N".format(i) for i in ylab]
            x_pos=list(map(self.num2lon,xlab))
            y_pos=list(map(self.num2lat,ylab))

            if len(self.config["show_data"].shape)==3:
                
                a=self.ax.imshow(self.show_info,origin="lower",extent=[0,self.draw_fig["xsize"],0,self.ysize],vmin=self.config["varmin"],vmax=self.config["varmax"],cmap=self.config["cmp_current"],interpolation="hermite")
            else:
                a=self.ax.imshow(self.show_info,origin="lower",extent=[0,self.draw_fig["xsize"],0,self.ysize],vmin=self.config["varmin"],vmax=self.config["varmax"],cmap=self.config["cmp_current"],interpolation="hermite")
            self.ax.set_xticks(x_pos)
            self.ax.set_yticks(y_pos)
            self.ax.set_xticklabels(xlabs,fontsize=8) 
            self.ax.set_yticklabels(ylabs,fontsize=8) 
            self.fig.colorbar(a,cax=self.colorbar_axes,orientation='vertical',fraction=0.05,pad=0.05)
            _, self.colorbar_axes = plt.gcf().get_axes()
            self.canvs.draw()
        except:
            pass
if __name__=="__main__":
    root = ttk.Window()
    root.update()
    root.resizable(width=False, height=False)
    ncdraw(root)
    root.mainloop()
