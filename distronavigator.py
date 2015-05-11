#!/usr/bin/python
# -*- coding: utf-8 -*-

import sip
sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
from time import sleep
import subprocess
import pwd
import re
import socket
import threading
import codecs
import unicodedata
import gc

user = pwd.getpwuid(subprocess.os.getuid())[ 0 ]      # определяем имя юзера
home_dir = pwd.getpwuid(subprocess.os.getuid())[ 5 ]  # ... и адрес его домашнего каталога
navigator_is = subprocess.os.path.exists(home_dir+'/.distronavigator')   # выясняем, существует ли конфигурационный каталог программы
navigator_dir = home_dir+'/.distronavigator'
if navigator_is == False:
    subprocess.call('cp -rf /usr/share/distronavigator/.distronavigator '+home_dir+' && tar -xf /usr/share/distronavigator/mpd.tar.gz -C '+navigator_dir+' && tar -xf /usr/share/distronavigator/mp.tar.gz -C '+navigator_dir+' && sed -i -e "s!user!'+user+'!g" '+navigator_dir+'/main/images_dir '+navigator_dir+'/sources/* && mkdir -p '+navigator_dir+'/repo/i586/RPMS.hasher '+navigator_dir+'/repo/SRPMS.hasher '+navigator_dir+'/repo/i586/base && genbasedir --topdir='+navigator_dir+'/repo i586 hasher',shell=True)  # если его нет, то создаём его - и прописываем путь к нему в некоторых файлах, а также создаём личный репозиторий
tmp_dir = '/tmp/.private/'+user+'/distronavigator'   # каталог программы в tmpfs
pics_dir = '/usr/share/distronavigator/pics'
brandings_dir = navigator_dir+'/brandings/brandings/' 
subprocess.call('mkdir -p '+tmp_dir, shell=True)
buttons=[]  #  список кнопок основной панели (для очистки при переходе на другую страницу)
tw_d = 0  # для удаления текстовых окон
mes_is = 0  # для удаления сообщений
var_br_edit = '' 
branches = ['t7---t7','p7---p7','t6---t6','p6---p6']
base_distros_mpd = ['distrocreator.cd---DistroCreator','tde-mini.cd---TDE-mini','wmsmall.cd---WMSmall','kde-lite.cd---KDE-lite','lxde-lite.cd---LXDE-lite']
base_distros_mp = ['tde.iso---tde.iso'] 
make_d = False  # идёт ли в данный момент сборка дистрибутива
make_b = False # идёт ли в данный момент сборка пакетов брендинга

# Открытие файла
def open_f(n,mode='r',tx='',out='',sl=''):
        f = codecs.open(n, encoding='utf-8', mode=mode) # открываем файл           
        if 'r' in mode:   # если требуется читать файл...
            exec eval("out+'=f.read()'+sl") in locals(),globals()  # ...то читаем (если указано - делим на строки) и создаём переменную для доступа к результату чтения
        if mode in ['w','a','r+']:  # если записывать...
            f.write(tx)  # ...то записываем
        f.close()
           
# Верхние кнопки
class Top(QPushButton):
    def re_color(self):
        if mp_mpd == 'mpd':            
            for x in ['projects','pkglists','branding','params','set_gui']:
                eval("top_"+x+".setStyleSheet ('Top:!hover { background-color:#359a51 } Top:hover { background-color: #11da33 }')")   # всем кнопкам - исходный цвет...                            
            self.setStyleSheet ('Top {background-color: #e9fbd5}') # ...но активной - другой
        else:
            for x in ['projects','pkglists','branding','params','set_gui']:
                eval("top_"+x+".setStyleSheet ('Top:!hover { background-color:#6d74d3 } Top:hover { background-color: #414abd }')")   # всем кнопкам - исходный цвет...                            
            self.setStyleSheet ('Top {background-color: #eeeff7}') # ...но активной - другой            
            
    def __init__(self,com,tx):
        super(Top, self).__init__(text=tx)                                      
        top_box.layout.addWidget(self)  # размещаем наверху
        self.clicked.connect(com)  # подключаем команду
        self.clicked.connect(self.re_color)  # управление цветом кнопок
                                 
# Кнопки справа
class But (QPushButton):
    def __init__(self,tx,com,parent,hint='',evil='false'): 
        super(But, self).__init__(parent,text=tx)  # создаём кнопку с текстом
        parent.layout.addWidget(self)  # размещаем
        self.setFixedSize(168,33)  # устанавливаем размер               
        self.clicked.connect(com)  # подключаем команду
        self.setProperty("evil", evil)        
        if parent == panel_action:  # если кнопка для панели действий, то вносим в список, требующийся для очистки этой панели
            buttons.append(self)
        if var_popup == 'True' and hint != '':  # если есть подсказка, то показываем её
            self.setToolTip(u'<table width="250"><tr><td ALIGN=CENTER>'+hint+'</td></tr></table>')                                     

# Новая страница
class Page ():
    def __init__(self, parent,z,t,i=0,expl_loc='',inter_loc='',pic_x=30,pic_y=10):
        global main_area
        global inter
        global buttons
        global insert_text
        root.setWindowTitle(t)  # заголовок страницы
        mes.hide()  # скрываем сообщение (если было на предыдущей странице)
        for butt in buttons:
            butt.setParent(None)   # очищаем панель действий         
            del butt            
        buttons = []  # обнуляем список кнопок  панели действий
        if 'insert_text' in globals():
            insert_text.setParent(None)
            del insert_text       
        if 'inter' in globals():
            inter.setParent(None)
            del inter  # удаляем интерактивную область, если она есть
        main_area.setGeometry(0,30,780,520)
        if i == 1:  # если нужна интерактивную область...
            eval(expl_loc)  # ...делим окно между ней и информационной областью
            inter = QLabel(root)
            eval(inter_loc)
            inter.show()
        if var_expls == 'True':
            image = QPixmap()   # показываем пояснения, если велено
            image.load(z)
            main_area.setPixmap(image)
            main_area.setContentsMargins(pic_x,pic_y,0,0)            
        button_re.hide()               
        button_re.show()
          
# Картинка
class Pic (QPixmap):
    def __init__(self,im,x=60,y=20):
        super(Pic, self).__init__() 
        self.load(im)  # берём картинку из указанного файла
        main_area.setPixmap(self)  # размещаем 
        main_area.setGeometry(x,y,780,540)  # ИСПРАВИТЬ!!!  
         
# Сообщения от программы
class Message (QPushButton):
    def del_d(self):   # скрытие сообщения при нажатии на него
        self.hide()
    def new_mes(self,tx,color='green'):
        self.hide()          
        self.setProperty('color',color)
        self.setText(tx)  # вводим (или заменяем, если уже было) текст сообщения
        self.adjustSize()  # подгоняем размер поля сообщения под его содержимое 
        self.setStyleSheet("Message[color='green'] { background-color: #7cfb4a } Message[color='purple'] { background-color: #bc3bec } Message[color='red'] { background-color: #d40732 } ")       
        self.show()      
    def __init__(self):  # создание поля для сообщения (одноразово, при запуске программы, без показа)
        super(Message, self).__init__(parent=what_project) 
        self.move(0,0)             
        self.clicked.connect(self.del_d)  # для скрытия сообщения
                                     
# Переключатели
class R_But(QGroupBox):         
    def __init__(self,x,y,w,h,func,parent,vis,r_list='',filename='',radiogroup='',checked=''):
        global rbuttons_list
        rbuttons_list = r_list
        if filename != '':
            open_f (n=filename,out='rbuttons_list',sl='.splitlines()')  # файл с информацией для всех радиокнопок
        scroll = QScrollArea(parent=inter)
        scroll.setGeometry(x,y,w,h)                
        super(R_But, self).__init__(parent=inter)   # создаём фрейм для радиокнопок                               
        if rbuttons_list != [u''] and rbuttons_list != []:
            self.layout = QVBoxLayout(self)
            self.layout.setSpacing(1)
            for line in rbuttons_list:
                line2 = line.split('---')    # отделяем условное название кнопки от текста, поясняющего её назначение
                a3 = line2[0].replace('-','_').replace(".","_")
                exec eval("a3+'_rb = QRadioButton(eval(vis))'") in locals(), globals()   #  создаём кнопку     
                self.layout.addWidget(eval(a3+'_rb'))   #  добавляем её во фрейм
                if radiogroup!='':      # если группа кнопок использует не один фрейм... 
                    radiogroup.addButton(eval(a3+"_rb"))  #...  
                d = "'"+line2[0]+"'"  # выясняем условное имя кнопки 
                eval(a3+'_rb.clicked.connect(lambda: '+func+'(rb_name='+d+'))')  # указываем функцию,работающую при нажатии на кнопку
            if  checked != '': # если нужно, чтобы какая-то кнопка была активна...
                open_f (n=checked,out='checked_rb')  # ...смотрим в конфиге, какая именно 
                if checked_rb != 'none' and checked_rb != '':
                    checked_rb2 = checked_rb.replace("-","_").replace(".","_")
                    eval (checked_rb2+'_rb.setChecked(True)')              
            scroll.setWidget(self)              
            scroll.show()            

# Группа чекбоксов
class CheckBox_Group (QGroupBox):    
    def change_var(self,i,value):  # при нажатии на чекбокс
        global list_False
        global list_True               
        if value == False:
            list_False.append(i)   # элемент перемещается из списка True в список False...
            list_True.remove(i)
        else:
            list_True.append(i)   # ...или наоборот
            list_False.remove(i)                                                        
    def __init__(self,lists,w,h,x=40,y=30):
        global list_False
        global list_True
        scroll = QScrollArea(parent=inter)
        scroll.setGeometry(x,y,w,h)        
        super(CheckBox_Group, self).__init__(parent=inter)
        self.move(x,y)        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)              
        list_True = []   # список элементов для отмеченных чекбоксов 
        list_False = []  # список элементов для неотмеченных чекбоксов
        for a,b in lists:
            open_f (n=a,out='l',sl='.splitlines()')                           
            for r in l:
                r1 = r.split('---')  # отделяем имя элемента от его описания
                r2=r1[0].replace('-','_').replace('.','_')  # из имени каждого элемента создаётся имя связанной с ним переменной 
                exec eval('''r2+"_ch = QCheckBox(parent=self,text=r1[1])"''') in globals(),locals()  # кнопки для каждого элемента                        
                eval (r2+'_ch.setFixedSize(200,13)')  # размер чекбокса
                eval(r2+'_ch.setChecked(eval(b))')  # ставим галочку или, если велено
                self.layout.addWidget(eval(r2+'_ch'))
                exec eval ("'list_'+b+'.append(r)'")  in locals(), globals()  # добавляем элемент в соответствующий список
                exec eval ('''r2+"_ch.clicked.connect(lambda: self.change_var(i=u'"+r+"',value="+r2+"_ch.isChecked()))"''')  in locals(), globals()  # соединяем чекбокс с функцией, запускаемой при нажатии на него             
        scroll.setWidget(self)              
        scroll.show()               
               
# Окно для текста
class Tx_wind (QTextEdit):
    def __init__(self,source,out,parent=None,font='Arial 12',mess='',butt=u"Записать",dis=0,w=280,h=372,x=30,y=40,del_end=False): 
        global but_wr
        global tw
        def wr():  # перезапись файла, из которого взят текст
            s1=unicode(self.toPlainText())
            open_f(n=source,mode='w',tx=s1+'\n')
            if del_end == True:  # если нужно, удаляем пустые строки в конце файла
                subprocess.call ("sed -i -e :a -e '/^\\n*$/{$d;N;ba' -e '}' "+source,shell=True)
            if mess != '':
                mes.new_mes(mess)
        def tw_destr():
            global tw_d
            tw_d = 0
        f = codecs.open(source, encoding='utf-8') # открываем файл...
        f2 = f.read()
        f.close()
        super(Tx_wind,self).__init__(parent=inter,plainText=f2)  # ...копируем текст из него в окно
        self.setGeometry(x,y,w,h)
        self.show()
        self.destroyed.connect(tw_destr) # сигнал при закрытии текстового окна              
        if tw_d == 1:        # нужно для открытия основного и родительского pkglist'а без замены страницы
            destr(but_wr)
            destr(tw)                        
            destr(tw)                        
        if butt != '':                
            but_wr = But(parent=panel_action,com=wr,tx=butt)

# Однострочное поле             
class Entry (QLineEdit):
    def __init__(self,x,y,width=200,height=20):
        super(Entry, self).__init__(parent=inter)        
        self.setGeometry(x,y,width,height)
        self.show() 
         
# Пояснительная надпись        
class Label (QLabel):
    def __init__(self,x,y,tx,parent): 
        super(Label, self).__init__(parent=parent,text=tx)
        self.move(x,y)                                
        self.show() 
        
# Пункт в настройках сборочницы или программы
class Sett (QCheckBox):
    def __init__(self,tx='',n='',var=''):
        exec ("def "+n+"(var=var):\n global var_"+n+"\n global var_expls\n global var_mp_mpd_choice\n global set_par\n open_f (n=navigator_dir+'/settings/"+n+"',mode='w',tx=str(var))\n var_"+n+" = str(var)\n if var_expls=='False':\n  tes = Pic(im='/usr/share/distronavigator/pics/explan/empty.png',x=20,y=80)\n elif set_par=='set':\n  Pic(im='/usr/share/distronavigator/pics/explan/set.png',x=0,y=130)\n if var_mp_mpd_choice=='True':\n  but_mp_mpd.show()\n else:\n  but_mp_mpd.hide()\n   ") in globals(), locals()  # создаём функцию, запускаемую при активации/деактивации пункта
        super(Sett, self).__init__(parent=inter,text=tx)  # создаём сам пункт 
        self.setChecked(eval(var))  # активируем, если велено
        inter.layout.addWidget(self)  # размещаем
        self.clicked.connect(eval(n))  # подключаем его к вышеупомянутой функции
        
# Отслеживание процесса сборки (дистрибутива или пакетов брендинга) 
class Observ(QObject):
    def ob(self,x):
        global make_d
        global make_b
        global src_branding_is       
        if x == 'mp_make_start':
            what_stat.setText(u"Сборка в m-p\nдистрибутива\n"+pr_visname2)
            make_d = True  # включаем индикатор, показывающий, что сейчас идёт сборка дистрибутива        
        if x == 'autoconf_err':
            show_report(tx=u"Не  удалось создать\nфайл configure",color='red')                           
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'configure_err':
            show_report(tx=u"Ошибка при \nконфигурировании\nдистрибутива",color='red')                           
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'make_err':
            show_report(tx=u"Сборка дистрибутива\n завершилась неудачно",color='red')                           
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'repo_err':
            all_repos()          
            top_params.re_color()           
            show_report(tx=u"Проверьте список\nрепозиториев",color='red')                           
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'clean_err':
            show_report(tx=u"Ошибка при очистке\n сборочницы",color='red')
        if x == 'break_d':
            show_report(tx=u"Процесс сборки\n  прерван",color='purple')
        if x == 'autoconf_start':
            what_stat.setText(u"Создание скрипта\nconfigure для\n"+pr_visname2)
            make_d = True  # включаем индикатор, показывающий, что сейчас идёт сборка дистрибутива
        if x == 'configure_start':
            what_stat.setText(u"Конфигирируется\nдистрибутив\n"+pr_visname2)
        if x == 'make_start':
            what_stat.setText(u"Идёт сборка\nдистрибутива\n"+pr_visname2)
        if x == 'make_ok':
            show_report(tx=u"Сборка успешно \nзавершена")                                         
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/ok.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'tar_err':
            show_report(tx=u"Не  удалось\nупаковать архив",color='red')                       
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 & ', shell=True)
        if x == 'srpmbuild_err':
            show_report(tx=u"Ошибка при создании\n srpm",color='red')                        
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'rpmbuild_err':
            show_report(tx=u"Ошибка при\n сборке rpm-пакетов",color='red')                        
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'genbasedir_err':
            show_report(tx=u"Ошибка при\n обновлении\nрепозитория",color='red')                       
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/er.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'tar_start':
            what_stat.setText(u"   Упаковка\n   исходников\nбрендинга в .tar")
            make_b = True  # включаем индикатор, показывающий, что сейчас идёт сборка пакетов брендинга
        if x == 'srpmbuild_start':
            what_stat.setText(u"Создаём \nsrpm-пакет\nбрендинга")
        if x == 'rpmbuild_start':
            what_stat.setText(u"Собираем \nrpm-пакеты\nбрендинга")
        if x == 'genbasedir_start':
            what_stat.setText(u"Обновление\nрепозитория")
        if x == 'break_b':
            show_report(tx=u"Сборка пакетов\nбрендинга  прервана")
            but_break_branding.hide()
            panel_log.hide()                        
        if x == 'branding_ok':
            show_report(tx=u"Пакеты брендинга\nв вашем репозитории\n обновлены")
            make_b = False 
            what_stat.setText(u"")
            but_break_branding.hide()                      
            if var_music == 'True':
                subprocess.call('mpg123 /usr/share/distronavigator/music/ok.mp3  > /dev/null 2>&1 &', shell=True)
        if x == 'get_start':
            what_stat.setText(u"Загрузка исходников\nклубного\nбрендинга")               
        if x == 'get_ok':
            what_stat.setText('')
            src_branding_is = 'True'
            brandings_pages()
            mes.new_mes (tx=u'Теперь можно\nсоздавать\nсвой брендинг')                                       
        if x == 'get_err':
            what_stat.setText('')
            mes.new_mes (tx=u'Не удалось загрузить\nисходники клубного\nбрендинга',color='red')                             
                                           
def active_project(rb_name):  # работает при выборе юзером какого-либо проекта 
    global project
    project = rb_name
    actproject()
        
def active_branch(rb_name):  # работает при выборе юзером какого-либо бранча
    global branch_var
    branch_var = rb_name 
    
def destr(n):  # удаление объекта   
    n.setParent(None)
    n.destroy() 
    
def top_but_equal():
    for x in ['projects','pkglists','branding','params','set_gui']:
        if mp_mpd == 'mpd':
            eval("top_"+x+".setStyleSheet ('Top:!hover {background-color:#359a51} Top:hover { background-color: #11da33 }')")   # всем кнопкам - исходный цвет...               
        else:
            eval("top_"+x+".setStyleSheet ('Top:!hover {background-color:#6d74d3} Top:hover { background-color: #414abd }')")   # всем кнопкам - исходный цвет...
            
def mp_mpd_switch(): # переключение между сборочными системами кнопкой
    global mp_mpd
    if make_d == True:
        mes.new_mes(tx=u'Нельзя переключаться\nна другую сборочницу\nво время сборки\nдистрибутива',color='purple')
    else:
        if mp_mpd == 'mp':
            mp_mpd = 'mpd'
        else:
            mp_mpd = 'mp'            
        mp_mpd_choice()                          
                
# Настройка программы под выбранную сборочную систему
def mp_mpd_choice():
    global mp_mpd
    global build_dir
    global conf_dir
    global conf_dir_0
    global base_distros
    global project
    build_dir = navigator_dir+'/'+mp_mpd
    conf_dir = navigator_dir+'/'+mp_mpd+'_conf'
    conf_dir_0 = '/usr/share/distronavigator/'+mp_mpd+'_conf' 
    but_mp_mpd.setText(mp_mpd)
    base_distros =  eval('base_distros_'+mp_mpd)
    open_f (n=conf_dir+'/default_project',out='default_project')  # определяем проект по умолчанию
    project = 'none'   # заглушка на случай отсутствия такового
    d = subprocess.os.path.exists(conf_dir+'/projects/'+default_project)  # проверяем его наличие 
    if d == True:
        project = default_project # устанавливаем проект по умолчанию 
    actproject()
    colors()
    main_page()
         
# Настройка программы под активный проект
def actproject():
    global pr_shortname
    global pr_visname
    global pr_parent
    global pr_branch   
    global pr_branding
    global pr_groups
    global pr_config
    global pr_live_install      
    pr_config = conf_dir+'/projects/'+project  #  определяем конфиг проекта
    open_f (n=pr_config,out='c',sl='.splitlines()')  # читаем его
    pr_shortname = c[0]  # краткое условное имя проекта
    pr_visname = c[1]  # отображаемое имя проекта
    pr_parent = c[2]  # краткое условное имя родительского проекта
    pr_branch = c[3]  #  бранч, на котором собирается проект
    pr_branding = c[4]  #  брендинг, с которым собирается проект
    pr_groups = c[5]  #  используются ли дополнительные группы пакетов
    pr_live_install = c[6]
    if project != 'none':           
        what_project.setText(u'В разработке проект:\n'+c[1]+'\n'+project) 
    else:
        what_project.setText('')
    what_project.show()                
                     
def colors():    
    main_color = QPalette()
    app.setStyleSheet("QCheckBox:hover { background-color: 3333ff }")
    if mp_mpd == 'mpd':
        main_color.setColor(QPalette.Window, QColor("#e9fbd5")) #  основной цвет
        app.setStyleSheet("But {background-color:'#dbfbb9'} But:hover { background-color: #aeffb1 } But[evil='true'] {background-color:'#ff4444'} But[evil='true']:hover {background-color:'#ff0000'} QGroupBox { border:0px } R_But {background-color:#e9fbd5} QScrollArea, R_But, CheckBox_Group {background-color:#e9fbd5} QScrollArea {border:0px}") 
        button_re.setStyleSheet("QPushButton {background-color:'#dbfbb9'} QPushButton:hover { background-color: #aeffb1 } ")
        but_mp_mpd.setStyleSheet("QPushButton {background-color:'#e9fbd5'} QPushButton:hover { background-color: #b4ee6f } ")
    else:
        main_color.setColor(QPalette.Window, QColor("#eeeff7")) #  основной цвет
        app.setStyleSheet("But {background-color:'#b9d5fb'} But:hover { background-color: #aeb2ff } But[evil='true'] {background-color:'#ff4444'} But[evil='true']:hover {background-color:'#ff0000'} QGroupBox { border:0px } R_But {background-color:#eeeff7} QScrollArea, R_But, CheckBox_Group {background-color:#eeeff7} QScrollArea {border:0px}") 
        button_re.setStyleSheet("QPushButton {background-color:'#b9d5fb'} QPushButton:hover { background-color: #aeb2ff } ") 
        but_mp_mpd.setStyleSheet("QPushButton {background-color:'#eeeff7'} QPushButton:hover { background-color: #8eb0fd } ")   
    root.setPalette(main_color)
    top_but_equal()

# Установка (или переустановка) m-p-d
def restor():
    global project
    project = 'none'  # не должно быть в это время активного проекта
    i = subprocess.Popen('rm -rf '+navigator_dir+'/projects '+navigator_dir+'/mpd '+conf_dir+'/cfg && cp -rf /usr/share/distronavigator/.distronavigator/cfg '+navigator_dir+' && cat /dev/null >' +navigator_dir+'/main/work_projects && cat /dev/null >'+navigator_dir+'/main/hid_projects  && echo -n "none" >'+conf_dir+'/default_project  && cp -rf /usr/share/distronavigator/.distronavigator/projects '+navigator_dir+' && tar xf /usr/share/distronavigator/mpd.tar.gz -C '+navigator_dir,shell = True)
    i.wait()  # удаляем каталог m-p-d и заменяем его "нулёвым", удаляем ещё списки проектов.
    if i.returncode == 0:
        mes.new_mes(tx=u'Сборочная система\nвосстановлена в\nпервоначальном виде')
        open_f (n=navigator_dir+'/main/images_dir',mode='w',tx='--with-outdir='+navigator_dir+'/my_images')
        what_project.setText(u' ')
        what_project.show()
    if i.returncode != 0:
        mes.new_mes(tx=u'Не удалось вернуть\nсборочную систему\nв первоначальное состояние')

# Проверка права юзера использовать хашер
def hasher():
    subprocess.call('groups > '+tmp_dir+'/ha',shell=True)
    open_f (n=tmp_dir+'/ha',out='h')  # ...проверяем наличие прав
    if 'hashman' not in h and user != 'root': 
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/hasher.png',i=1,expl_loc='main_area.setGeometry(0,32,780,520)',inter_loc='inter.setGeometry(62,273,580,60)',t=u"Использование хашера")  # ...если нет, предлагаем юзеру получить права
        st = QTextEdit(parent=inter)
        st.setGeometry(0,0,400,60)
        st.setText(u'su-\n<тут впишите пароль root>\nhasher-useradd '+user)
        st.show()
        s = subprocess.Popen('xterm &',shell=True)

def browser_ch(): # выбор браузера
    global browser
    for x in ['firefox','chromium','opera','kdebase-konqueror']: 
        q = subprocess.Popen('rpm -q '+x+' > /dev/null 2>&1',shell=True)
        q.wait()
        if q.returncode == 0:
            browser = x
            break 
    
def panel_action_show():
    panel_action.adjustSize()   
    panel_action.show() 
    
# Очистка сборочницы
def distclean(x='hh'):
    global th_clean
    global clea
    class Mycl (QObject):
        def run(self): 
            what_stat.setText(u"Производится\n очистка\nсборочницы")
            subprocess.os.chdir(build_dir)
            cl = subprocess.Popen('make distclean > /dev/null 2>&1', shell=True)
            cl.wait()
            if cl.returncode == 0:                        
                what_stat.setText(u"Очистка\nсборочницы\nзавершена") 
                sleep(5)
                what_stat.setText(" ")                      
            else:
                self.connect(self,QtCore.SIGNAL('valueChanged(QString)'),observer.ob)
                self.emit(QtCore.SIGNAL('valueChanged(QString)'),'clean_err')   
    th_clean = QThread()    # создаём поток для процесса очистки
    clea = Mycl()
    clea.moveToThread(th_clean)
    th_clean.started.connect(clea.run)
    th_clean.start()

def show_report(tx,color='green'):     # сообщения о том, чем завершилась сборка
    global make_d
    global make_b
    mes.new_mes(tx=tx,color=color)
    what_stat.setText(' ')
    if make_d == True:  # если шла сборка дистрибутива, а не брендинга, запускаем послесборочную функцию
        post()
    make_d = False
    make_b = False   
    
def break_mk_distro2():
    break_mk_distro()

def break_branding2():
    break_branding()
    
def log():  # журнал сборки дистрибутива
    global tw
    global but_log
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/projects_no.png',i=1,expl_loc='main_area.setGeometry(0,400,790,60)',inter_loc='inter.setGeometry(0,40,790,450)',t=u'Журнал процесса сборки')
    tw = Tx_wind (source=build_dir+'/build.log',out='log_file',h=420,w=730,x=10,y=10,font='Arial 12',dis=1,butt='')
    panel_action.hide()
    top_but_equal()
    but_log.hide()
    if make_d == True:
        but_log_re.show()

def log_re():  # обновление журнала
    destr(tw)
    if make_d == False:
        panel_log.hide()
    log()
    
def log_report():                 # показывает отчёт о завершённой сборке
    log()
    but_log_report.hide()
    but_break_mk_distro.hide()
    panel_log.hide() 

def log_restore():
    if make_b == False:
        panel_log.hide()
        but_log_report.hide()  # скрываем кнопку отчёта о сборке (если юзер не хочет его смотреть)
        but_log_re.hide()    
        if make_d == True:  
            but_log.show() # заменяем кнопку обновления журнала кнопкой его просмотра
            panel_log.adjustSize()
            panel_log.show()                    
                                                                                
############### Секция "Проекты" ####################

def projects(tr=0):
    
    global but_all_projects
      
    def new_project():
    # Создание нового проекта
    # Терминология :
    # Отображаемое имя проекта - произвольное (можно кириллицей); отображается в окне программы, но в самом коде не используется.
    # Условное имя проекта - то, которое фигурирует в Makefile.
    # Краткое имя проекта - основное без .cd/.dvd.
        global cd_dvd        
        global src_var
        global branch_var
        global active_project
        global src_f
        global active_branch
        global pr_f 
        global radiogroup1
           
        def create_project(event):
            global branch_var                                               
            if entry_vis.text() == '':            # Должно быть выбрано отображаемое имя проекта
                mes.new_mes(tx=u'Не указано \nотображаемое \nимя проекта',color='purple')
            elif entry_n.text() == '':              # Должно быть выбрано условное имя проекта
                mes.new_mes(tx=u'Не указано \nусловное имя проекта',color='purple')
            elif entry_n.text() in ['distrocreator','tde-mini','wmsmall','kde-lite','lxde-lite']: 
                mes.new_mes(tx=u'Условное имя \nпроекта не должно\nсовпадать с именем\nбазового дистрибутива',color='purple')
            elif ' ' in entry_n.text():
                mes.new_mes(tx=u'Недопустимое\nусловное имя\nпроекта',color='purple')
            else:           # создаётся проект                                 
                s0 = src_var.split('.')
                if src_var in ['distrocreator.cd','wmsmall.cd','tde-mini.cd','kde-lite.cd','lxde-lite.cd']:                          
                    parent_begin = s0[0] + '-@BRANCH@.' + s0[1]    #   определяем начало строки родительского проекта в Makefile.in
                    s0[0] = s0[0] + '-' + branch_var
                    new_short = str(entry_n.text())+'-'+ branch_var # краткое условное имя нового проекта
                    cfg_end = ''
                else:   # если родительский проект - тоже пользовательский                      
                    parent_begin = src_var
                    branch_var = parent_begin.split('-')[-1].replace('.cd','').replace('.dvd','')
                    new_short = str(entry_n.text())+'-'+branch_var 
                    cfg_end = '-'+branch_var                    
                new = new_short+'.'+str(cd_dvd.currentText())  # полное условное имя нового проекта 
                pr_is = subprocess.os.path.exists (conf_dir+'/projects/'+new)  # нет ли уже проекта с таким именем
                if pr_is == True:
                    mes.new_mes(tx=u"Проект с таким\nименем уже есть",color='purple')
                else:
                    variants = [' install2 main install-', ' use-'+new_short+'-live live install2 main install-', ' rescue install2 main install-',' use-'+new_short+'-live live rescue install2 main install-', ' use-'+new_short+'-live  live live-', ' use-'+new_short+'-live use-live-install install2 live live-']
                    string_middle = variants[instal_live.currentIndex()]
                    open_f (n=build_dir+'/Makefile.in',out='mk',sl='.splitlines()')
                    for x in mk:              
                        if x.startswith(parent_begin+': |'):       # Из Makefile.in вылавливаем описание родительского проекта
                            parent_string = x
                            if instal_live.currentIndex() in [4,5]: # если создаём Live, то строка родительского дистрибутива не нужна
                                str_new = new+': |'+string_middle+cd_dvd.currentText().replace('dvd','dvd5').replace('.','')+'.@IMAGETYPE@'
                            else:   # если Install, то нужна                                                               
                                str_new = x.replace(parent_begin+': | ',new+': | use-'+new_short+' ').replace('@BRANCH@',branch_var).replace(' main ',' ').replace(' live ',' ').replace(' install2 ',' ').replace(' install-dvd5.','').replace(' install-cd.','').replace('live-cd.','').replace('live-dvd5.','').replace('@IMAGETYPE@',string_middle+cd_dvd.currentText().replace('dvd','dvd5').replace('.','')+'.@IMAGETYPE@')  # на его основе создаём описание нового... 
                            break
                    open_f (n=build_dir+'/Makefile.in',mode='a',tx=str_new+'\n')  #  добавляем его в Makefile.in               
                    subprocess.call("sed -i '9s/PRODUCTS = /PRODUCTS = "+new+" /' "+build_dir+'/Makefile.in',shell=True)  # ...и его основное имя вносится туда же (в список PRODUCTS)                       
                    open_f (n=conf_dir+'/cfg/'+s0[0].replace('-t7','').replace('-p6','').replace('-t7','').replace('-p7','')+cfg_end, out='x2')  # На основе секции родительского проекта в configure.ac создаётся секция нового проекта...
                    y2=x2.replace(src_var,new).replace('-branch-',branch_var).replace(s0[0],new_short)
                    open_f (n=tmp_dir+'/cfg',mode='w',tx=y2)
                    open_f (n=conf_dir+'/cfg/'+new_short,mode='w',tx=y2) #...и вносится в '+conf_dir+'/cfg...
                    subprocess.call('sed -i "/:-\\\"lite.cd\\\"};;/r '+tmp_dir+'/cfg" '+build_dir+'/configure.ac', shell=True)      # ....и в configure.ac
                    subprocess.call("sed -i -e '24s/use-gdm  /use-gdm  "+new_short+' '+new_short+'-main '" /' "+build_dir+"/use.mk.in", shell=True) # вписываем новый проект в use.mk.in
                    subprocess.call('touch '+build_dir+'/profiles/pkg/lists/'+new_short+' '+conf_dir+'/projects/'+new+'-groups && ln -s '+build_dir+'/profiles/pkg/lists/'+new_short+' '+build_dir+'/profiles/pkg/lists/'+new_short+'-main > /dev/null 2>&1',shell=True) # создаём нужные для проекта файлы 
                    if instal_live.currentIndex() in [0,2]:
                        distro_type = 'install'
                    elif instal_live.currentIndex() in [1,3]:
                        distro_type = 'install_live'
                    else:
                        distro_type = 'live'                        
                    project_conf = new_short+'\n'+unicode(entry_vis.text())+'\n'+src_var.replace('.dvd','').replace('.cd','')+'\n'+branch_var+'\n\nFalse\n'+distro_type+'\n'  # текст для конфига проекта
                    open_f(n=conf_dir+'/projects/'+new,mode='w',tx=project_conf)  # записываем этот конфиг
                    open_f (n=conf_dir+'/work_projects',mode='a',tx=new+'---'+unicode(entry_vis.text())+'\n') # добавляем проект в список проектов 
                    if instal_live.currentIndex() in [1,3,4,5]:
                        prof_list = []                       
                        for x in parent_string.split(' '):
                            if x.startswith('use-'):
                                prof_list.append(x.replace('use-','').replace('@BRANCH@',branch_var))
                        open_f (n=conf_dir_0+'/use_live',out='use0')  # из шаблона делаем  новый абзац для use.mk.in
                        use1 = use0.replace('project',new_short).replace('prof_string',' '.join(prof_list)).replace('mark',new +'-live')
                        open_f (n=tmp_dir+'/ul',mode='w',tx=use1)
                        subprocess.call('cat '+tmp_dir+'/ul >> '+build_dir+'/use.mk.in', shell=True)
                        subprocess.call('touch '+build_dir+'/profiles/pkg/lists/'+new_short+'-live',shell=True)
                    projects()           
        
        def src_f(rb_name): 
            global src_var
            global branch_var
            src_var = rb_name  # определяем имя родительского проекта
            if src_var in ['distrocreator.cd','wmsmall.cd','tde-mini.cd','kde-lite.cd','lxde-lite.cd']: # выясняем, базовый он или нет...
                for x in ['p6_rb','t6_rb','p7_rb','t7_rb']:  
                    eval(x+'.setDisabled(False)')   # активируем...
            else:        
                for x in ['p6_rb','t6_rb','p7_rb','t7_rb']:  
                    eval(x+'.setDisabled(True)')   # ...или деактивируем радиокнопки выбора бранчей 
                    branch_var = ''
                           
        # Интерфейс для создания нового проекта
        if mp_mpd == 'mp':
            mes.new_mes(tx=u'В m-p это ещё\nне работает :(',color='purple')
        else:
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/new_project.png',i=1,expl_loc='main_area.setGeometry(0,410,780,150)',inter_loc='inter.setGeometry(0,40,780,350)',t=u"Создание нового проекта")
            panel_action.hide()        
            but_create_project = But(parent=panel_action,com=create_project,tx=u'Создать\nпроект')         
            panel_action_show()
            src_var = 'distrocreator.cd'
            branch_var = 't7' 
            radiogroup1 = QButtonGroup()
            fr_base_distros = R_But(x=15,y=40,h=180,w=140,r_list=base_distros,parent=inter,func='src_f',vis='line2[1]',radiogroup=radiogroup1)
            fr_branches = R_But(x=165,y=40,h=140,w=70,parent=inter,r_list=branches,func='active_branch',vis='line2[1]')
            fr_my_projects = R_But(x=290,y=40,h=310,w=240,filename=conf_dir+'/work_projects',parent=inter,func='src_f',vis='line2[1]',radiogroup=radiogroup1) 
            base_distro_label = Label (parent=inter,x=35,y=20,tx=u'Базовые дистрибутивы')
            my_projects_label = Label (parent=inter,x=320,y=20,tx=u'Ваши проекты')
            vis_name_label = Label (parent=inter,x=547,y=50,tx=u'Отображаемое имя проекта')
            cond_name_label = Label (parent=inter,x=560,y=120,tx=u'Условное имя проекта')
            distro_type_label = Label (parent=inter,x=560,y=190,tx=u'Тип целевого дистрибутива')               
            entry_vis = Entry(x=542,y=70,width=208)  # Поле ввода отображаемого имени проекта                          
            entry_n = Entry(x=542,y=140,width=154)  # Поле ввода краткого имени проекта               
            cd_dvd = QComboBox(inter)  #  Выбор между cd- и dvd-вариантами
            cd_dvd.setGeometry(700,140,50,20)
            cd_dvd.show()
            cd_dvd.addItem("cd")
            cd_dvd.addItem("dvd")
            instal_live = QComboBox(inter)  #  Выбор между cd- и dvd-вариантами
            instal_live.setGeometry(542,210,238,20)
            instal_live.show()
            instal_live.addItem(u"Установочный")
            instal_live.addItem(u"Установочный+Live")
            instal_live.addItem(u"Установочный+Rescue") 
            instal_live.addItem(u"Установочный+Live+Rescue")
            instal_live.addItem(u"Live")   
            instal_live.addItem(u"Live с возможностью установки")                       
            t7_rb.setChecked(True)
            distrocreator_cd_rb.setChecked(True)
        
    # Показ всех проектов - рабочих и скрытых - с возможностью превращения первых во вторые и наоборот
    def all_projects():
        global fr_all_projects
        global but_projects_hide
        global but_all_projects
                               
        # Подтверждение изменений в статусе проектов
        def commit_pr():
            if project in u'\n'.join(list_False):
                mes.new_mes(tx=u'Нельзя скрывать\nактивный проект',color='purple')
            else:
                open_f (n=conf_dir+'/hid_projects',mode='w',tx=u'\n'.join(list_False)+'\n')
                open_f (n=conf_dir+'/work_projects',mode='w',tx=u'\n'.join(list_True)+'\n')  # Рабочие и скрытые проекты прописываются в свои конфиги
                if list_False == []:
                    open_f (n=conf_dir+'/hid_projects',mode='w',tx='')
                if list_True == []:
                    open_f (n=conf_dir+'/work_projects',mode='w',tx='')                
                projects()        
               
        # Скрытие полного списка проектов
        def projects_hide():
            but_hide_pr.destroy()
            but_com.destroy()
            fr_all_projects.destroy()
            but_show_pr.show()
            but_trash.destroy()

        # Корзина для скрытых проектов
        def trash():
            global fr_trash
            global list_True           
            
            def del_projects():   # удаление проектов
                global project
                for a in list_True:
                    x = a.split('---')[0]
                    x_0 = x.replace('.cd','').replace('.dvd','')                    
                    open_f (n=conf_dir+'/projects/'+x+'-groups',out='grs',sl='.splitlines()')
                    for g in grs:
                        g2 = g.split("---")[0]
                        subprocess.call("rm -rf "+build_dir+"/profiles/pkg/lists/"+x_0+"-"+g2+" "+build_dir+"/profiles/pkg/groups/"+x_0+"-"+g2+".directory",shell=True)  # удаляем файлы групп пакетов проекта (если есть)                    
                    subprocess.call("rm -rf "+conf_dir+'/projects/'+x+" "+conf_dir+'/projects/'+x+"-groups "+build_dir+"/profiles/pkg/lists/"+x_0+" "+build_dir+"/profiles/pkg/lists/"+x_0+"-main "+ navigator_dir+"/cfg/"+x_0+" && "+ "sed -i -e \'/"+x+": | /d\' -e \'10s/"+x+"//\' "+build_dir+"/Makefile.in",shell=True)  # удаляем каталог проекта, его pkglist, шаблон, записи в Makefile.in
                open_f (n=conf_dir+'/hid_projects',mode='w',tx='\n'.join(list_False)+'\n')  #  переписывается файл-список скрытых проектов
                if list_False == []:
                    open_f (n=conf_dir+'/hid_projects',mode='w',tx='')
                    destr(fr_trash)                                          
                trash() 
                
            def no_del():      # выход из корзины
                projects() # указываем не создавать кнопку показа всех проектов
                all_projects()
                
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/trash.png',i=1,expl_loc='main_area.setGeometry(0,320,780,240)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Корзина')
            panel_action.hide()
            but_del_projects = But(parent=panel_action,com=del_projects,tx=u'Удалить\nуказанные проекты')
            but_no_del = But(parent=panel_action,com=no_del,tx=u'Ничего\nне делать')
            panel_action_show()
            fr_trash = CheckBox_Group (lists=[(conf_dir+'/hid_projects','False')],h=300,w=200)
                                                                     
         # Показ всех проектов                  
        fr_all_projects = CheckBox_Group (lists=([conf_dir+'/work_projects','True'],[conf_dir+'/hid_projects','False']),x=480,y=20,h=300,w=250)
        panel_action.layout.removeWidget(buttons[-1])     
        buttons[-1].setParent(None)
        del buttons[-1]
        panel_action.hide()
        but_projects_hide=But(parent=panel_action,com=projects,tx=u'Скрыть полный\nсписок проектов')
        but_commit_pr=But(parent=panel_action,com=commit_pr,tx=u'Применить\nизменения',hint=u'Отмеченные проекты будут на виду, неотмеченные - в корзине')       
        but_trash = But(parent=panel_action,com=trash,tx=u'Корзина')                          
        panel_action_show()
        
    def def_project():
        open_f (n=conf_dir+'/default_project',mode='w',tx=project)
        open_f (n=conf_dir+'/projects/'+project,out='z',sl='.splitlines()')
        mes.new_mes(tx=u'Проект по умолчанию -\n '+z[1])
        if project == 'none':
            mes.new_mes(tx=u'Проект по умолчанию \n не выбран',color='purple')
        
    # Управление параметрами сборки
    def mk_params():
        global str_mk_tmpfs
        open_f (n=navigator_dir+'/settings/tmpfs_d',out='tm')  # использовать ли tmpfs
        str_mk_tmpfs = " TMP=0"
        if tm == 'True':
            str_mk_tmpfs = "TMP="+tmp_dir+"/mkimage-work-dir"   # указание для make использовать tmpfs
        open_f (n=conf_dir+'/str_mk_tmpfs',mode='w',tx=str_mk_tmpfs)    # .....она записывается в файл '+conf_dir+'/str_mk_tmpfs        
    
    ######  Подготовка и запуск процесса сборки
    def pre_start():
        global observer
        global start
        global make_d
        global show_report
        global choice_project
        global branch_var
        global post
        global pr_visname2
           
        # Действия после завершения (успешного или нет) процесса сборки
        def post():
            panel_log.hide()  
            but_log.hide()  # скрытие кнопок, которые нужны только в ходе сборки
            but_log_re.hide()
            but_break_mk_distro.hide()
            but_log_report.show()
            panel_log.adjustSize()   
            panel_log.show()
            
        # Запуск процесса сборки
        def start():
            global choice_project
            global m_clean
            global str_mk_tmpfs
            global make_d
            global make_b
            global distro_run
            global distro_thread
            global Distro_run
            global observer
            global but_break_mk_distro
                                            
            # Создание потока для управления процессом сборки
            class Distro_run(QObject):
                def run(self):
                    global break_mk_distro
                    global distro_run
                    global distro_thread
                    global next_command
                    global break_by_user 
                    
                    def break_mk_distro():  # принимаем и выполняем приказ прервать сборку
                        global break_by_user
                        global u  
                        break_by_user = True
                        u.terminate()  # прерывание сборки                       
                    
                    def ex(com,mes_err,signal,make=False): # выполняем команды конфигурирования, сборки, очистки
                        global break_by_user
                        global u
                        global next_command
                        self.emit(QtCore.SIGNAL('valueChanged(QString)'),signal)
                        sleep(1)
                        u=subprocess.Popen(com, shell=True)  # выполняем команду
                        u.wait()
                        if u.returncode != 0:                # если  выполнение команды завершилось неудачно...
                            next_command = False
                            if break_by_user == True:  # если сборка была прервана пользователем...
                                self.emit(QtCore.SIGNAL('valueChanged(QString)'),'break_d') # сообщаем об прерывании...                                
                            else:
                                sleep(0.1)
                                subprocess.call('tail build.log > '+tmp_dir+'/end_log', shell=True)       
                                log = open(tmp_dir+'/end_log').read()    # проверяем журнал сборки...
                                if 'base/pkglist' in log:              #... не из-за отсутствия ли репозиториев упала.... 
                                    self.emit(QtCore.SIGNAL('valueChanged(QString)'),'repo_err')    # .... если да, так и рапортуем...    
                                else:                
                                    self.emit(QtCore.SIGNAL('valueChanged(QString)'),mes_err)  # если нет - сообщаем о неудаче сборки без уточнений
                            clean_post()   # смотрим, выполнять ли очистку            
                        else:  #  если команда выполнена успешно
                            if make == True:                       # если выполнялась команда make...
                                subprocess.call('tail build.log > '+tmp_dir+'/end_log', shell=True)       
                                log = open(tmp_dir+'/end_log').read()    # проверяем журнал сборки...
                                if ' finished.targets' in log or 'Written to medium' in log:              #...чтобы выяснить, успешна ли она 
                                    self.emit(QtCore.SIGNAL('valueChanged(QString)'),"make_ok")
                                else:                                       #.... сообщаем результат проверки
                                    self.emit(QtCore.SIGNAL('valueChanged(QString)'),"make_err")
                                clean_post()   # смотрим, выполнять ли очистку                            
                        
                    def clean_post():  # очистка сборочницы (если нужно)
                        if m_clean == 'True':       # смотрим, включена ли опция очистки
                            sleep(0.1)
                            self.connect(self,QtCore.SIGNAL('valueChanged(QString)'),distclean) # ....и запускаем её
                            self.emit(QtCore.SIGNAL('valueChanged(QString)'),'bububu')                           

                    next_command = True
                    break_by_user = False      # индикатор, показывающий, завершилась ли сборка сама или была прервана пользователем
                    subprocess.os.chdir(build_dir)     # переходим в рабочий каталог сборочницы
                    self.connect(self,QtCore.SIGNAL('valueChanged(QString)'),observer.ob)                    
                    if mp_mpd == 'mpd':                 
                        ex(com ='autoconf > build.log 2>&1', mes_err='autoconf_err',signal='autoconf_start')   # создаём скрипт configure
                        if next_command == True:
                            ex(com = configure_str,mes_err='configure_err',signal='configure_start')         # конфигурируем дистрибутив
                        if next_command == True:   
                            subprocess.call('mkdir -p '+tmp_dir+'/mkimage-work-dir',shell=True) 
                            ex(com = make_str,mes_err='make_err',make=True,signal='make_start')          # выполняем его сборку
                    else:
                        ex(com ='BUILDLOG='+build_dir+'/build.log IMAGEDIR='+outdir_mp+' APTCONF='+navigator_dir+'/sources/apt.conf-'+nl2+'-'+bran+' make '+distr, mes_err='make_err',make=True,signal='mp_make_start')                      
            
            branch = ' '
            open_f (n=navigator_dir+'/main/branch',out='bran')  #  смотрим, какой бранч используется
            nn = 1          
            open_f (n=navigator_dir+'/sources/my_repos-'+bran,out='t2',sl='.splitlines()')          
            for i in t2:
                if 'rpm' not in i:   #  проверка, не забыл ли юзер указать репозитории для данного бранча
                    nn = 0
            if nn == 05:
                all_repos() # переход на страницу указания репозиториев
                top_params.re_color()
                mes.new_mes(tx=u"Похоже, не указаны\nрепозитории.\nПереходим туда,\nгде их можно указать",color='purple')
            elif make_d == True:
                mes.new_mes(tx=u"Нельзя одновременно\nсобирать два дистрибутива",color='purple')  
            elif make_b == True:
                mes.new_mes(tx=u"Нельзя одновременно\nсобирать дистрибутив\nи пакеты брендинга",color='purple')   
            else:
                branc = ' --with-version='+bran  # от этого зависит указание бранча в названии сборки и выбор репозиториев для сборки
                open_f (n=navigator_dir+'/sources/local_net-'+bran,out='nl2') # выбор списка репозиториев
                apt_conf = ' --with-aptconf='+navigator_dir+'/sources/apt.conf-'+nl2+'-'+bran+' '
                mk_params()   #  выясняются установленные параметры сборки
                subprocess.call('echo -n "" > '+build_dir+'/build.log',shell=True)  # удаляется журнал предыдущей сборки (иначе возможны странности)       
                open_f (n=navigator_dir+'/brandings/one_sev',out='br')  
                str_branding = ''
                if br == 'one':  # если для всех проектов используется один брендинг...
                    open_f (n=navigator_dir+'/brandings/common_branding',out='x')  # ...выясняем, какой именно
                    str_branding = '--with-branding='+x
                elif br == 'sev':  # а если разные...
                    str_branding = '--with-branding='+pr_branding  # ...выясняем иначе
                open_f (n=navigator_dir+'/main/images_dir',out='outdir')  # каталог для готовых образов
                outdir_mp = outdir.replace('--with-outdir=','')
                configure_str = './configure '+str_branding+' '+outdir+' --with-distro='+distr+branc+apt_conf+' >> build.log 2>&1' # строка запуска configure
                nice19 = ''
                open_f (n=navigator_dir+'/settings/nice',out='nice') # ограничение жадности
                if nice == 'True':
                    nice19 = 'nice -n 19'
                make_str = str_mk_tmpfs+' '+nice19+' make '+distr+' >> build.log 2>&1' # строка запуска сборки дистрибутива
                open_f (n=navigator_dir+'/settings/clean',out='m_clean') # нужна ли очистка после сборки
                but_break_mk_distro.show()
                but_log.show()
                panel_log.resize(174,75)
                panel_log.show()
                distro_run = Distro_run()
                distro_thread = QThread()
                distro_run.moveToThread(distro_thread)
                distro_thread.started.connect(distro_run.run)
                distro_thread.start()


        # Подготовка к запуску процесса сборки
        if choice_project == 'base':
            if base_var  == 'none':   # проверяем, указаны ли дистрибутив и бранч
                mes.new_mes(tx=u"Дистрибутив\nне выбран",color='purple') 
            elif branch_var == '':
                mes.new_mes(tx=u"Бранч\nне выбран",color='purple')
            else:               
                e = base_var.split('.')
                distr = e[0]+'-'+branch_var+'.'+e[1]  # вычисляем название требуемого дистрибутива
                pr_visname2 = distr
                open_f (n=navigator_dir+'/main/branch',mode='w',tx=branch_var) #  вписываем в конфиг указанный юзером бранч
                mes.hide()
                start()
        else:   #  если собирается пользовательский дистрибутив
            distr = project
            if  distr == 'none':  # проверяем, указан ли он
                mes.new_mes(tx=u"Проект не выбран",color='purple')
            else:
                pr_visname2 = pr_visname
                open_f (n=navigator_dir+'/main/branch',mode='w',tx=pr_branch)   #  ... и вписываем бранч в конфиг
                mes.hide()
                start()

    # Страница запуска
    def mk_distr():
        # запуск процесса сборки указанного базового дистрибутива
        def base_start():
            global choice_project
            but_log_report.hide()
            choice_project = 'base'   # указание на то, что собираться будет именно базовый дистрибутив
            pre_start()                   # запускается обычный процесс сборки

        def a_start():
            global choice_project
            but_log_report.hide()
            choice_project = ''   # указание на то, что собираться будет именно активный дистрибутив
            pre_start()                   # запускается обычный процесс сборки

        def show_baseprojects(): # страница запуска при возможности собирать и базовые дистрибутивы
            global base_var
            global branch_var
            global active_branch
            global src_f
            
            def src_f(rb_name):
                global base_var
                base_var = rb_name      
                
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/mk_projects.png',i=1,expl_loc='main_area.setGeometry(0,330,780,270)',inter_loc='inter.setGeometry(0,40,780,270)',t=u'Запуск процесса сборки')
            panel_action.hide()
            but_start = But(parent=panel_action,com=a_start,tx=u"Превратить активный\nпроект в дистрибутив",hint=u'Собрать дистрибутив на основе проекта, указанного над этой кнопкой')
            but_base_start = But (parent=panel_action,com=base_start,tx=u"Собрать указанный\nбазовый дистрибутив",hint=u'Собрать тот базовый дистрибутив, который выбран в списке слева, на указанном там же бранче')
            but_hide_baseprojects = But (parent=panel_action,com=hide_baseprojects,tx=u"Скрыть список базовых\nдистрибутивов")
            but_distclean  = But (parent=panel_action,com=distclean,tx=u"Очистить\nсборочницу",hint=u'Нажмите сюда, если процесс сборки обрывается, едва начавшись')
            fr_base_distros = R_But(x=50,y=70,h=250,w=140,r_list=base_distros,parent=inter,func='src_f',vis='line2[1]')
            fr_branches = R_But(x=245,y=70,h=200,w=170,parent=inter,r_list=branches,func='active_branch',vis='line2[1]')
            base_var = 'none'
            branch_var = ''
            panel_action_show()

        def hide_baseprojects():
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/mk_projects.png',i=1,expl_loc='main_area.setGeometry(0,330,780,270)',inter_loc='inter.setGeometry(0,40,780,270)',t=u'Запуск процесса сборки')
            panel_action.hide()
            but_start = But(parent=panel_action,com=a_start,tx=u"Превратить активный\nпроект в дистрибутив",hint=u'Собрать дистрибутив на основе проекта, указанного над этой кнопкой')
            but_show_baseprojects = But  (parent=panel_action,com=show_baseprojects,tx=u"Показать список\nбазовых дистрибутивов")
            but_distclean  = But(parent=panel_action,com=distclean,tx=u"Очистить\nсборочницу",hint=u'Нажмите сюда, если процесс сборки обрывается, едва начавшись')
            panel_action_show()

        show_basepr = open(navigator_dir+'/settings/baseprojects').read()
        if show_basepr == 'True':
            show_baseprojects()
        else:
            hide_baseprojects()

    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/projects.png',i=1,expl_loc='main_area.setGeometry(0,370,780,190)',inter_loc='inter.setGeometry(0,40,780,330)',t=u'Проекты')        
    if var_expls == 'True':
        work_projects = open(conf_dir+'/work_projects')
        wp = work_projects.read()
        if wp == '':
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/projects_no.png',i=1,expl_loc='main_area.setGeometry(0,300,780,260)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Проекты')     # пояснения показываются в зависимости от того, если ли уже хоть один проект                            
    fr_projects = R_But(x=40,y=20,h=300,w=360,filename=conf_dir+'/work_projects',parent=inter,func='active_project',vis='line2[1]',checked=conf_dir+'/default_project')            
    what_branding.setText('')
    panel_action.hide()
    if tr == 0:    # кнопка показа всех проектов не создаётся, если функция вызвана из корзины
        but_mk_distr=But(parent=panel_action,com=mk_distr,tx=u'Собрать\nдистрибутив')
        but_new_project=But(parent=panel_action,com=new_project,tx=u'Новый\nпроект')
        but_def_project = But(parent=panel_action,com=def_project,tx=u'Назначить\nпроект основным',hint=u'Указать, чтобы активный в данный момент проект был активен и при запуске программы')
        but_all_projects = But(parent=panel_action,com=all_projects,tx=u'Показать\nвсе проекты')
        #if project != 'none':
            #eval (project.replace('.','_').replace('-','_')+'_rb.setChecked(True)')        
    else:
        but_mk_distr=But(parent=panel_action,com=mk_distr,tx=u'Собрать\nдистрибутив')
        but_new_project=But(parent=panel_action,com=new_project,tx=u'Новый\nпроект')
        but_def_project = But(parent=panel_action,com=def_project,tx=u'Назначить\nпроект основным',hint=u'Указать, чтобы активный в данный момент проект был активен и при запуске программы')        
    panel_action_show() 
    log_restore()          
    
################## Состав сборки  ###############

def pkglists():
        global all_pkglists

        # Открытие  pkglist'а активного проекта
        def my_pkglist():            
            if project == 'none':
                mes.new_mes(tx=u"Проект не выбран",color='purple')
            else:
                global tw_d
                global tw
                panel_action.hide()
                if mp_mpd == 'mpd':               
                    tw = Tx_wind (source=build_dir+'/profiles/pkg/lists/'+pr_shortname,out='file_text',h=240,w=400,x=250,y=3,font='Arial 14',mess=u'Список пакетов\nобновлён')
                else:
                    tw = Tx_wind (source=build_dir+'/pkg.in/lists/nav/'+pr_shortname.replace('.iso',''),out='file_text',h=240,w=400,x=250,y=3,font='Arial 14',mess=u'Список пакетов\nобновлён')                    
                tw_d = 1
                panel_action_show()
               
        # Открытие  pkglist'а родительского проекта
        def parent_pkglist():
            if project == 'none':
                mes.new_mes(tx=u"Проект не выбран",color='purple')
            else:
                global tw_d
                global tw
                panel_action.hide()
                a = ''
                if mp_mpd == 'mpd':                
                    e = subprocess.os.path.exists(build_dir+'/profiles/pkg/lists/'+pr_parent+'-'+pr_branch+'.in')
                    if e == True:
                        a = '.in'               
                    tw = Tx_wind (source=build_dir+'/profiles/pkg/lists/'+pr_parent.replace('-t6','').replace('-p6','').replace('-t7','').replace('-p7','')+'-'+pr_branch+a,out='file_text',h=240,w=400,x=250,y=3,font='Arial 14',mess=u'Список пакетов\nобновлён')
                else:
                    tw = Tx_wind (source=build_dir+'/pkg.in/lists/nav/'+pr_parent.replace('-t6','').replace('-p6','').replace('-t7','').replace('-p7','').replace('.iso','')+'-'+pr_branch+a,out='file_text',h=240,w=400,x=250,y=3,font='Arial 14',mess=u'Список пакетов\nобновлён')    
                tw_d = 1
                panel_action_show()
                
        # Открытие  pkglist'а Live
        def live_pkglist():
            def live_parent():
                def live_re():
                    live_pkglist()
                page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/live.png',i=1,expl_loc='main_area.setGeometry(0,460,780,80)',inter_loc='inter.setGeometry(0,40,780,420)',t=u'Живой диск')                         
                tw = Tx_wind (source=build_dir+'/profiles/pkg/lists/live-'+pr_branch+'.in',out='file_text',h=330,w=400,x=250,y=3,font='Arial 14',mess=u'Список пакетов\nобновлён')
                but2 = But(parent=panel_action,com=live_re,tx=u"Ваши дополнения\nк списку пакетов")
                panel_action.resize(174,75)
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/live.png',i=1,expl_loc='main_area.setGeometry(0,460,780,80)',inter_loc='inter.setGeometry(0,40,780,420)',t=u'Живой диск') 
            panel_action.hide()              
            tw = Tx_wind (source=build_dir+'/profiles/pkg/lists/'+pr_shortname+'-live',out='file_text',h=330,w=400,x=250,y=3,font='Arial 14',mess=u'Список пакетов\nобновлён')        
            but_p = But(parent=panel_action,com=live_parent,tx=u"Базовый список\nпакетов")
            but_synaptic = But(parent=panel_action,com=synaptic,tx=u"Запустить\nСинаптик")
            but_pkg=But(parent=panel_action,com=pkglists,tx=u"Пакеты\n(Основная страница)")
            panel_action_show()

        # Дополнительные группы пакетов
        def addon_pkglists():            
            global add_group2
            global group_com
            global group_var
            def add_group2(nnn=''):
                
                global d_act
                addon_pkglists()
                add_group(pkgs=nnn)  

            # Открытие  дополнительного pkglist'а
            def edit_group():
                global group_var
                
                #   Добавление шаблона группы пакетов
                def add_draft():
                    def create_draft():  # создание шаблона из дополнительной группы пакетов
                        if entry_n.text() != '' and entry_vis.text() != '' and descr.toPlainText() != '':  # если все поля заполнены
                            subprocess.call('cp '+build_dir+'/profiles/pkg/lists/'+project.replace('.cd','').replace('.dvd','')+'-'+group_var+' '+conf_dir+'/drafts/'+str(entry_n.text()),shell=True) # копируем файл группы в файл шаблона
                            subprocess.call('echo -n  "'+str(entry_n.text())+'---'+unicode(entry_vis.text())+'---     '+unicode(descr.toPlainText()).replace('\n','     ')+'\n" >> '+conf_dir+'/drafts',shell=True) # добавляем имя и описание шаблона к список шаблонов
                            drafts()  # переходим на страницу шаблонов
                    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/cr_draft.png',i=1,expl_loc='main_area.setGeometry(0,350,780,210)',inter_loc='inter.setGeometry(0,40,780,300)',t=u'Создание шаблона группы')
                    entry_n = Entry(x=50,y=80,width=200,height=20)
                    entry_vis = Entry(x=50,y=160,width=200,height=20)
                    descr = QTextEdit(parent=inter)
                    descr.setGeometry(320,60,385,230)
                    descr.show()
                    name_label = Label(parent=inter,x=69,y=60,tx=u'Условное имя шаблона')
                    vis_label = Label(parent=inter,x=54,y=140,tx=u'Отображаемое имя шаблона')
                    descr_label = Label(parent=inter,x=430,y=40,tx=u'Описание шаблона')
                    but1 = But(parent=panel_action,com=create_draft,tx=u"Создать шаблон\nиз группы")
                    but2 = But(parent=panel_action,com=edit_group,tx=u"Ничего\nне делать")
                    panel_action.resize(174,75)
                if group_var == 'none':
                    mes.new_mes(tx=u"Группа не выбрана",color='purple')
                else:
                    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/add_gr.png',i=1,expl_loc='main_area.setGeometry(0,490,780,70)',inter_loc='inter.setGeometry(0,40,780,440)',t=u'Дополнительная группа пакетов')
                    tw = Tx_wind (source=build_dir+'/profiles/pkg/lists/'+pr_shortname+'-'+group_var,out='file_text',h=400,w=545,x=50,y=10,font='Arial 14',del_end=True,mess=u'Список пакетов\nобновлён')  
                    but_1 = But(parent=panel_action,com=add_draft,tx=u"Создать шаблон\nиз группы")
                    but_2 = But(parent=panel_action,com=addon_pkglists,tx=u"К списку\nгрупп")
                    but_synaptic = But(parent=panel_action,com=synaptic,tx=u"Запустить\nСинаптик")
                    panel_action.resize(174,145)

            # Создание новой группы пакетов
            def add_group(en='',pkgs=''):
                def create_group():
                    if unicode(entry_group_descr .text()) == '' or str(entry_group_name.text()) == '':
                       mes.new_mes(tx=u"Заполните\nвсе поля",color='purple')
                    else:
                        open_f(n=conf_dir_0+'/group',out='g0')  # открываем шаблон файла описания группы
                        g3 = g0.replace('gr_name',str(str(entry_group_name.text()))).replace('description',unicode(entry_group_descr.text())).replace('distro',pr_shortname) # делаем из шаблона описание группы
                        subprocess.call('echo '+'\"'+g3+'\"'+' >> '+build_dir+'/profiles/pkg/groups/'+pr_shortname+'-'+str(entry_group_name.text())+'.directory',shell=True)   # забрасываем его куда надо                     
                        open_f(n=build_dir+'/profiles/pkg/lists/'+pr_shortname+'-'+str(entry_group_name.text()),mode='w',tx=pkgs) # создаём пустой файл пакетов этой группы и, если группа создаётся из шаблона, копируем его туда
                        open_f (n=pr_config+'-groups',mode='a',tx=str(entry_group_name.text())+'---'+unicode(entry_group_descr.text())+'\n') # вписываем в конфиг групп проекта новую группу
                        open_f(n=conf_dir+'/projects/'+project+'-groups',out='gr_nam',sl='.splitlines()')
                        mm1 = []
                        mm2 = []
                        for x in gr_nam:
                            y = pr_shortname + '-' + x.split('---')[0]
                            z = 'disk-'+pr_shortname+'-'+x.split('---')[0]
                            mm1.append(y)
                            mm2.append(z)
                        string1 = ' '.join(mm1)
                        string2 = ' '.join(mm2) 
                        u = open(conf_dir_0+'/use')                                               
                        use0 = u.read()                   # из шаблона делаем  новый абзац для use.mk.in
                        use5 = use0.replace('name1',pr_shortname).replace('name2',pr_shortname+'-main').replace('mark',project+'--').replace('string1',string1).replace('string2',string1)
                        open_f(n=tmp_dir+'/jk',mode='w',tx=use5)
                        subprocess.call('sed -i -e"/#--'+project+'--/d" '+build_dir+'/use.mk.in', shell=True) # удаляем из файла use.mk.in старый вариант абзаца
                        subprocess.call('cat '+tmp_dir+'/jk >> '+build_dir+'/use.mk.in', shell=True) #записываем новый абзац в  use.mk.in 
                        subprocess.call('sed -i "/'+project+':/s/main/main\ disk-'+pr_shortname+'-'+str(entry_group_name.text())+'/" '+build_dir+'/Makefile.in',shell=True)  #  вписываем новую группу в Makefile.in
                        addon_pkglists()

                page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/add_group.png',i=1,expl_loc='main_area.setGeometry(0,320,780,280)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Дополнительная группа пакетов') 
                entry_group_descr = Entry (x=40,y=60,width=300)  # поле для описания группы
                entry_group_name = Entry (x=40,y=120) # поле для имени группы
                group_descr_label = Label (parent=inter,x=70,y=40,tx=u'Описание группы ') 
                group_name_label = Label (parent=inter,x=60,y=100,tx=u'Название группы')                           
                panel_action.hide()
                but_create = But(parent=panel_action,com=create_group,tx=u"Создать\nгруппу")
                but_no = But(parent=panel_action,com=addon_pkglists,tx=u"Не создавать\nгруппу")
                panel_action_show()

            def del_group():   # удаление группы
                global group_var
                subprocess.call('sed -i "/^'+group_var+'---/d" '+pr_config+'-groups',shell=True)
                subprocess.call("sed -i 's/disk-"+pr_shortname+"-"+group_var+" /\ / ' "+build_dir+'/Makefile.in',shell=True)
                subprocess.call("sed -i 's/"+pr_shortname+"-"+group_var+" / /' "+build_dir+'/use.mk.in',shell=True)
                addon_pkglists()

            # Шаблоны групп
            def drafts():
                global fr_drafts
                global var_draft
                global draft_com
                global radiogroup1
                
                def look_draft(descr=''):   # просмотр шаблона                   
                    def help_draft_to_group(event):
                        Help_all(c=2,s='Создать группу, по составу совпадающую с данным шаблоном.')
                    if var_draft != '':  # если юзер выбрал какой-то шаблон...
                        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/draft.png',i=1,expl_loc='main_area.setGeometry(0,410,780,150)',inter_loc='inter.setGeometry(0,40,780,360)',t=u'Шаблоны групп пакетов')  
                        panel_action.hide()                                            
                        if var_draft in my_drafts:  # ...причём он пользовательский...
                            #expl = Pic(im='draft.png',insert=descr,coord='+25+100')  
                            tw = Tx_wind (source=conf_dir+'/drafts/'+var_draft,out='file_text',h=362,w=545,x=100,y=30,font='Arial 14',butt=u"Перезаписать",mess=u'Список пакетов\nобновлён')   # ...то открываем его с возможностью правки                            
                        elif var_draft in base_drafts:                                                     # а если штатный...
                            #expl = Pic(im='draft.png',insert=descr,coord='+25+70')
                            tw = Tx_wind (source=conf_dir_0+'/drafts/'+var_draft,out='file_text',h=362,w=545,x=100,y=30,font='Arial 14', dis=1)  # ...то открываем read-only                        
                        but1 = But(parent=panel_action,com=add_group,tx=u"Создать группу\nиз шаблона")
                        but2 = But(parent=panel_action,com=drafts,tx=u"Список\nшаблонов") 
                        panel_action_show()
                                                   
                    else:
                        mes.new_mes(tx=u'Шаблон\nне указан',color='purple')

                def del_draft():       # удаление шаблона
                    global var_draft                    
                    if var_draft == '':
                        mes.new_mes(tx=u"Шаблон\nне указан",color='purple')
                    elif var_draft in my_drafts:  # если выбран пользовательский шаблон...
                        subprocess.call('rm -f '+conf_dir+'/drafts/'+var_draft,shell=True) # ...удаляем его файл
                        subprocess.call('sed -i "/'+var_draft+'--/d" '+conf_dir+'/drafts',shell=True) #
                        drafts()     
                    else:
                        mes.new_mes(tx=u"Удалять можно лишь\nсозданные вами шаблоны",color='purple')

                def draft_com(rb_name):
                    global var_draft
                    var_draft = rb_name
                
                page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/drafts.png',i=1,expl_loc='main_area.setGeometry(0,320,780,240)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Шаблоны групп пакетов')
                radiogroup1 = QButtonGroup()
                fr_drafts1 = R_But(x=60,y=40,h=300,w=140,filename='/usr/share/distronavigator/main/drafts',parent=inter,func='draft_com',vis='line2[1]',radiogroup=radiogroup1)
                fr_drafts2 = R_But(x=260,y=40,h=300,w=140,filename=conf_dir+'/drafts',parent=inter,func='draft_com',vis='line2[1]',radiogroup=radiogroup1)
                staff_drafts_label = Label (parent=inter,x=70,y=20,tx=u'Штатные шаблоны')
                my_drafts_label = Label (parent=inter,x=285,y=20,tx=u'Мои шаблоны')
                my_drafts = []
                base_drafts = []
                open_f(n='/usr/share/distronavigator/main/drafts',out='descr1',sl='.splitlines()')
                open_f(n=conf_dir+'/drafts',out='descr2',sl='.splitlines()')
                for x in descr1:
                    nn = x.split('---')        # отделяем названия групп от описаний
                    base_drafts.append(nn[0])
                for x in descr2:
                    nn = x.split('---')
                    my_drafts.append(nn[0])                
                var_draft = ''
                but_look = But(parent=panel_action,com=look_draft,tx=u"Просмотреть\nвыбранный шаблон")
                but_del = But(parent=panel_action,com=del_draft,tx=u"Удалить\nвыбранный шаблон")
                but_no = But(parent=panel_action,com=addon_pkglists,tx=u"К списку\nгрупп")
                panel_action.resize(174,109)
                
            if project == 'none':  # страница дополнительных групп
                mes.new_mes(tx=u"Проект не выбран",color='purple')
            else :
                page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/add_groups.png',i=1,expl_loc='main_area.setGeometry(0,400,780,160)',inter_loc='inter.setGeometry(0,40,780,340)',t=u'Дополнительные группы пакетов')
                
                def group_com(rb_name):   # указываем, какая группа сейчас должна обрабатываться
                    global group_var
                    group_var = rb_name
                fr_groups = R_But(x=70,y=35,h=300,w=540,filename=pr_config+'-groups',parent=inter,func='group_com',vis='line2[1]')              
                gr_names = []
                group_var = 'none'
                panel_action.hide()
                but_add = But(parent=panel_action,com=add_group,tx=u"Добавить\nгруппу")
                but_del = But(parent=panel_action,com=del_group,tx=u"Удалить\nвыбранную группу")
                but_edit = But(parent=panel_action,com=edit_group,tx=u"Редактировать\nвыбранную группу")
                but_drafts = But(parent=panel_action,com=drafts,tx=u"Шаблоны\nгрупп")
                but_pkg=But(parent=panel_action,com=pkglists,tx=u"Пакеты (основная\nстраница)")
                panel_action_show()

        def synaptic():
            subprocess.call('synaptic &', shell=True)

        def gr_is(rb_name):   # включение или отключение использования дополнительных групп пакетов
            if project == 'none':
                mes.new_mes(tx=u'Проект не выбран',color='purple')
            else:    
                subprocess.call("sed -i '6c"+str(rb_name)+"' "+pr_config,shell=True)  # записываем в конфиг, использовать ли дополнительные группы
                open_f(n=pr_config+'-groups',out='g1',sl='.splitlines()') # открываем файл с перечнем групп
                g2 = []
                g3 = []
                but_add_pkg.hide()
                panel_action.hide()
                if rb_name == True:  # если указано использовать дополнительные группы...
                    for x in g1:
                        y = x.split('---')
                        g2.append(pr_shortname+'-'+y[0])  # составляем список групп для use.mk.in...
                        g3.append('disk-'+pr_shortname+'-'+y[0])  # ... и для Makefile.in
                    but_add_pkg.show()
                panel_action_show() 
                string2 = ' '.join(g2)   # превращаем список групп в строку
                string3 = ' '.join(g3)                
                open_f(n=build_dir+'/use.mk.in',out='usm2',sl='.splitlines()') 
                subprocess.call("sed -i -e '/"+project+": |/s/ main .* install-/ main install-/' -e '/"+project+": |/s/ main / main "+string3+" /' "+build_dir+"/Makefile.in",shell=True)  #  подправляем описание дистрибутива в Makefile.in              

        # Кнопки секции "Пакеты"
        global but_show_pkg
        actproject()
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/pkgs.png',t=u'Пакеты',i=1,expl_loc='main_area.setGeometry(0,310,750,280)',inter_loc='inter.setGeometry(0,40,780,250)') 
        if pr_live_install != 'live':
            ch_gr = QCheckBox(parent=inter,text=u'Использовать\nдополнительные\nгруппы программ')
            ch_gr.setGeometry(40,40,280,93)
            ch_gr.clicked.connect(lambda: gr_is(rb_name=ch_gr.isChecked()))
            ch_gr.setChecked(eval(pr_groups))        
            ch_gr.show()  
        subprocess.call("sed '/"+project+": |/w "+tmp_dir+"/gr6' "+build_dir+"/Makefile.in > /dev/null 2>&1",shell=True)
        panel_action.hide()
        but_mypkg = But(parent=panel_action,com=my_pkglist,tx=u"Ваш основной\nсписок пакетов",hint=u'Список пакетов, добавленных вами к тем, которые уже есть в базовом дистрибутиве.')
        but_basepkg = But(parent=panel_action,com=parent_pkglist,tx=u"Базовый\nсписок пакетов",hint=u'Такой же список, но относящийся к базовому дистрибутиву. Изменять его нежелательно.') 
        but_add_pkg = But(parent=panel_action,com=addon_pkglists,tx=u"Дополнительные\nгруппы пакетов",hint=u'Группы программ, которые устанавливаются только по указанию пользователя.')      
        if pr_live_install == 'install_live': # кнопку live-режима показываем лишь если этот режим в проекте включен
            but_live=But(parent=panel_action,com=live_pkglist,tx=u"Живой \nдиск")
        but_synaptic = But(parent=panel_action,com=synaptic,tx=u"Запустить\nСинаптик",hint=u'Весьма удобно для добавления пакетов в профиль, особенно если не вполне точно помните, как они называются  - просто копируйте их названия из свойств пакета в Синаптике :) ')
        if pr_groups == 'False':
            but_add_pkg.hide()
        panel_action_show()
        log_restore() 
        what_branding.setText('')  
                           
# Установка исходников клубного брендинга
def src_branding_get():
    global get_thread
    global get_run
    global src_branding_is 
    d = QMessageBox()         
    a = QtGui.QMessageBox.question(d, u'Установить исходники клубного брендинга?',u"Для создания своего брендинга необходимы исходные тексты брендинга Клуба активных пользователей ALT Linux. Установить их?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
    if a == QtGui.QMessageBox.Yes:

        class Thread_get(QObject):
            def run(self):
                subprocess.os.chdir(brandings_dir+'club_branding')   # переходим в каталог для клубного брендинга
                self.connect(self,QtCore.SIGNAL('valueChanged(QString)'),observer.ob) 
                self.emit(QtCore.SIGNAL('valueChanged(QString)'),'get_start')                
                u=subprocess.Popen('wget http://altclub.100ms.ru/Repo_p7/SRPMS.hasher/branding-altlinux-club-small-6.0.1-alt22.src.rpm && rpm2cpio branding-altlinux-club-small-6.0.1-alt22.src.rpm | cpio -i  && tar -xf branding.tar && mv -f branding.spec branding && rm -rf branding-altlinux-club-small-6.0.1-alt22.src.rpm branding.tar && cp -f /usr/share/distronavigator/main/release-notes.ru.html.in branding/notes && echo -n "True" > '+navigator_dir+'/main/src_branding', shell=True)      # выполняем команду
                u.wait()
                if u.returncode == 0:
                     self.emit(QtCore.SIGNAL('valueChanged(QString)'),'get_ok') 
                else:
                    self.emit(QtCore.SIGNAL('valueChanged(QString)'),'get_err')
                                          
    get_thread = QThread()
    get_run = Thread_get()
    get_run.moveToThread(get_thread)
    get_thread.started.connect(get_run.run)                
    get_thread.start()                                        
    d.show()                        

# Какую именно страницу открывать при нажатии кнопки "Оформление"        
def brandings_pages():
    global var_brandings_use
    global var_brandings_edit
    global various_headbands
    open_f (n=navigator_dir+'/brandings/headbands',out='various_headbands') # предлагать ли выбор между общей заставкой и разными
    open_f (n=navigator_dir+'/settings/brandings_use',out='vv')
    var_brandings_use = vv
    open_f (n=navigator_dir+'/settings/brandings_edit',out='dd')
    var_brandings_edit = dd
    what_branding.setText('')
    if var_brandings_use == 'True':  # показывать ли страницу выбора брендингов для использования
        brandings_use()
    elif src_branding_is == 'False':
        src_branding_get()
    elif var_brandings_edit == 'True':  # показывать ли страницу выбора брендингов для редактирования
        brandings_edit()
    else:
        branding()
    log_restore()     
                 
def demo():  # переход в секцию брендинга в демо-режиме       
    branding(demo_mode=1) 
           
def demo_re():  # возврат в демо-режим
    branding(demo_mode=1,demo_mode2=1)
           
####### Выбор брендингов для использования  ########
def brandings_use():
    global no_brandings_use
    global br_edit_wr
    global one_sev
    global def_bgh
    global one_b
    global common_branding 
    
    def no_brandings_use():        # отключение показа этой страницы
        global var_brandings_use
        open_f (n=navigator_dir+'/settings/brandings_use',mode='w',tx='False')
        var_brandings_use = 'False'
        if src_branding_is == 'False':
            src_branding_get()
        else:         
            branding()

    def def_br(t):
        open_f (n=navigator_dir+'/brandings/use_def',mode='w',tx=str(t)) # ...записываем это в конфиг
        one_rb.setDisabled(t)   # деактивируем радиокнопки выбора брендингов
        sev_rb.setDisabled(t)               
        if t == True:    # если указано использовать родные брендинги дистрибутивов...
            panel_action.layout.removeWidget(buttons[-1])     
            buttons[-1].setParent(None)  # скрываем кнопку выбора
            del buttons[-1]
            panel_action.resize(174,212)
        else:         #   если выбор брендингов разрешён.....
            open_f (n=navigator_dir+'/brandings/one_sev',mode='w',tx='one')
            one_rb.setChecked(True)
            but_one_branding = But(parent=panel_action,com=assign_common_branding,tx=u'Всегда использовать\nвыбранный брендинг')       # показываем одну из кнопок выбора
            panel_action.resize(174,246)

    #  Использовать ли общий для всех  проектов брендинг
    def one_sev(rb_name):
        open_f (n=navigator_dir+'/brandings/one_sev',mode='w',tx=rb_name)
        if  rb_name == 'one':    # если указано использовать общий брендинг...
            panel_action.layout.removeWidget(buttons[-1])     
            buttons[-1].setParent(None)
            del buttons[-1]
            but_one_branding = But(parent=panel_action,com=assign_common_branding,tx=u'Всегда использовать\nвыбранный брендинг')  #  ....показываем  кнопку его назначения
        if  rb_name == 'sev':       # если указано для каждого проекта использовать отдельный брендинг
            panel_action.layout.removeWidget(buttons[-1])     
            buttons[-1].setParent(None)
            del buttons[-1]
            but_one_branding = But(parent=panel_action,com=assign_separ_branding,tx=u'Выбранный брендинг -\n активному проекту')            

    # Назначение общего брендинга
    def assign_common_branding():        
        if common_branding == '':     # если юзер не выбрал брендинг...
            mes.new_mes(tx=u"Брендинг не выбран",color='purple')   # ...просим выбрать
        else:    # если выбрал...
            open_f (n=navigator_dir+'/brandings/common_branding',mode='w',tx=common_branding) # ...вписываем в конфиг
            mes.new_mes(tx=u"Для всех сборок\nбудет использоваться\nбрендинг\n"+common_branding)

    # Привязка указанного брендинга к активному проекту
    def assign_separ_branding():
        if common_branding == '':     # если юзер не выбрал брендинг.....
            mes.new_mes(tx=u"Брендинг не выбран",color='purple')    # ...просим выбрать
        elif  project == 'none':     # ... если нет активного проекта
            mes.new_mes(tx=u"Проект не выбран",color='purple')    # ...просим выбрать
        else:   # если выбрал, то вписываем в конфиг активного проекта имя брендинга
            subprocess.call("sed -i '5c"+common_branding+"' "+pr_config,shell=True)  # записываем в конфиг проекта его брендинг
            open_f (n=pr_config,out='cnf',sl='.splitlines()')
            mes.new_mes(tx=u"Для проекта\n"+unicode(cnf[1])+u"\nназначен брендинг\n"+common_branding)
            
    #  Выбор готовых брендингов из репозиториев
    def other_brandings():
        global oth_branding
        global common_branding
        global o_branding
        
        def for_all_distros():
            global o_branding
            if o_branding == '':
                mes.new_mes (tx=u'Брендинг\n не выбран',color='purple')
            else:
                open_f (n=navigator_dir+'/brandings/common_branding',mode='w',tx=o_branding)
                mes.new_mes(tx=u"Для всех сборок\nбудет использоваться\nбрендинг\n"+o_branding)
            
        def for_one_distros():
            global o_branding
            if o_branding == '':
                mes.new_mes (tx=u'Брендинг\n не выбран',color='purple')
            elif project == 'none':
                mes.new_mes (tx=u'Нет активного\nпроекта',color='purple')                
            else:            
                subprocess.call("sed -i '5c"+o_branding+"' "+pr_config,shell=True)  # записываем в конфиг проекта его брендинг
                open_f (n=pr_config,out='cnf',sl='.splitlines()')
                mes.new_mes(tx=u"Для проекта\n"+unicode(cnf[1])+u"\nназначен брендинг\n"+o_branding)
            
        def oth_branding(rb_name):
            global o_branding
            o_branding = rb_name
            
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/other_brandings.png',i=1,expl_loc='main_area.setGeometry(0,320,780,240)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Выбор брендингов для использования из репозиториев') 
        fr_groups = R_But(x=60,y=28,h=200,w=340,filename='/usr/share/distronavigator/main/other_brandings',parent=inter,func='oth_branding',vis='line2[1]')
        o_branding = ''
        open_f (n=navigator_dir+'/brandings/common_branding',out='common_branding')  # выясняем, определён ли какой-то общий брендинг        
        if common_branding+'---'+common_branding in oth_br:
            eval (common_branding.replace('-','_')+'_rb.setChecked(True)')
            o_branding = common_branding  
        but_for_all_distros = But(parent=panel_action,tx=u"Использовать для\nвсех дистрибутивов",com=for_all_distros)
        if src_branding_is == 'True':               
            but_for_one_distros = But(parent=panel_action,tx=u"Использовать для\nактивного проекта",com=for_one_distros)
        panel_action.resize(174,75)
        
    def br_edit_wr(rb_name):
        global common_branding
        common_branding = rb_name
                                        
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/br_use.png',i=1,expl_loc='main_area.setGeometry(0,330,780,230)',inter_loc='inter.setGeometry(0,40,780,270)',t=u'Выбор брендингов для использования')
    panel_action.hide()
    but_new_branding =  But(parent=panel_action,tx=u"Создать новый\nбрендинг",com=new_branding)
    common_branding = ''
    open_f (n='/usr/share/distronavigator/main/other_brandings',out='oth_br',sl='.splitlines()')     
    if src_branding_is == 'True':
        br_edit=''
        open_f (n=navigator_dir+'/brandings/my_brandings',out='my_br',sl='.splitlines()')  #  список брендингов юзера
        if my_br != []:
            open_f (n=tmp_dir+'/all_br',mode='w',tx=u'club_branding---Клубный брендинг\n'+'\n'.join(my_br)+'\n')  # добавляем к нему клубный брендинг
        else:
            open_f (n=tmp_dir+'/all_br',mode='w',tx=u'club_branding---Клубный брендинг')   
        fr_all_brandings = R_But(x=30,y=30,h=240,w=340,filename=tmp_dir+'/all_br',parent=inter,func='br_edit_wr',vis='line2[1]')  #  фрейм для брендингов       
        fr_4 = R_But(x=400,y=100,h=100,w=420,r_list=[u'one---Использовать один брендинг для всех проектов', u'sev---Для каждого проекта выбирать брендинг отдельно'],checked=navigator_dir+'/brandings/one_sev',parent=inter,func='one_sev',vis='line2[1]')  # один брендинг для всех проектов или разные   
        open_f (n=navigator_dir+'/brandings/common_branding',out='common_branding')  # выясняем, определён ли какой-то общий брендинг
        if common_branding != '' and common_branding+'---'+common_branding not in oth_br:
            eval (common_branding.replace('-','_')+'_rb.setChecked(True)')
        open_f (n=navigator_dir+'/brandings/use_def',out='uf')  # ....разрешён ли выбор брендингов
        ch_def_br = QCheckBox(parent=inter,text=u'Использовать для каждого\nпроекта его брендинг по умолчанию')
        ch_def_br.setFixedSize(380,53)
        ch_def_br.move(410,40)
        ch_def_br.setChecked(eval(uf))
        ch_def_br.clicked.connect(lambda: def_br(t=ch_def_br.isChecked())) 
        ch_def_br.show()
        one_rb.setDisabled(eval(uf))
        sev_rb.setDisabled(eval(uf))        
        but_demo = But(parent=panel_action,tx=u"Демо-режим",com=demo)
        if var_brandings_edit == 'True':
            but_edit_branding = But(parent=panel_action,tx=u"Выбор брендингов\nдля редактирования",com=brandings_edit)
        but_delete_brandings = But(parent=panel_action,tx=u"Удалить\nлишние брендинги",com=delete_brandings)
        if uf == 'False':
            open_f (n=navigator_dir+'/brandings/one_sev',out='os')
            if os == 'one':
                but_one_branding = But(parent=panel_action,tx=u"Всегда использовать\nвыбранный брендинг",com=assign_common_branding)
            else:   
                but_separ_branding = But(parent=panel_action,tx=u"Выбранный брендинг -\n активному проекту",com=assign_separ_branding)        
    but_other_brandings = But(parent=panel_action,tx=u"Выбрать брендинг\nиз репозиториев",com=other_brandings)
    but_no_brandings_use = But(parent=panel_action,tx=u"Не показывать\nэту страницу",com=no_brandings_use)
    panel_action_show()

####### Выбор брендингов для редактирования  ########
def brandings_edit():
    global bm
    global var_br_edit
    global no_brandings_edit
    global br_edit_wr
                    
    def w_branding():        
        if var_br_edit == '':
            mes.new_mes(tx=u"Брендинг не выбран",color='purple')
        else:
            branding(wb=1)

    def no_brandings_edit():        # отключение показа этой страницы
        open_f (n=navigator_dir+'/settings/brandings_edit',mode='w',tx='False')
        var_brandings_edit = 'False'
        branding()

    def main_branding():
        
        if var_br_edit != '':
            open_f (n=navigator_dir+'/brandings/main',mode='w',tx=var_br_edit)
            mes.new_mes(tx=u"По умолчанию для\nредактирования будет\nоткрываться брендинг\n"+var_br_edit)
        else:
            mes.new_mes(tx=u"Брендинг не выбран",color='purple')
            
    def br_edit_wr(rb_name):
        global var_br_edit
        var_br_edit = rb_name
                               
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/br_edit.png',i=1,expl_loc='main_area.setGeometry(0,360,780,200)',inter_loc='inter.setGeometry(0,40,780,300)',t=u'Выбор брендингов для редактирования')
    panel_action.hide()     
    fr_my_brandings = R_But(x=40,y=30,h=260,w=450,filename=navigator_dir+'/brandings/my_brandings',parent=inter,func='br_edit_wr',vis='line2[1]',checked=navigator_dir+'/brandings/main')
    open_f (n=navigator_dir+'/brandings/main',out='var_br_edit')
    but_new_branding =  But(parent=panel_action,tx=u"Создать новый\nбрендинг",com=new_branding)
    but_my_branding = But(parent=panel_action,tx=u"Править выбранный\n  брендинг",com=w_branding)
    but_demo = But(parent=panel_action,tx=u"Демо-режим",com=demo)
    if var_brandings_use == 'True':
        but_edit_branding = But(parent=panel_action,tx=u"Выбор брендингов\nдля использования",com=brandings_use)
    but_delete_brandings = But(parent=panel_action,tx=u"Удалить\nлишние брендинги",com=delete_brandings)
    but_no_brandings_edit = But(parent=panel_action,tx=u"Не показывать\nэту страницу",com=no_brandings_edit)
    but_main_branding = But(parent=panel_action,tx=u"Назначить выбранный\nбрендинг основным",com=main_branding)       
    panel_action_show()

# Создание нового брендинга
def new_branding():
    global active_branch
    global br_choice
    global branch_var
    global src_br
    
    if src_branding_is == 'False':
       src_branding_get()
    else:        
    
        def create_branding():
            global branch_var
            global src_br 
            j = 0        
            for x in [entry_name,entry_theme,entry_release]:
                if x.text() == '':                    
                    mes.new_mes(tx=u"Заполните все\nпомеченные\nзвёздочкой поля",color='purple')
                    j = 1
            if j == 0:      
                br_n = str(entry_name.text())    # считываем введённые юзером названия...
                br_theme = str(entry_theme.text())
                br_version = str(entry_version.text())
                br_release = str(entry_release.text())
                my_name = str(entry_my_name.text())
                email = str(entry_email.text())
                new_br = br_n + '-' + br_theme  # ...из двух первых собираем имя брендинга
                br_dir1 = brandings_dir+new_br # определяем его каталог
                new_br_full = new_br + '-' + br_version # полное (с версией) имя брендинга... 
                if br_release != '':
                    new_br_full = new_br + '-' + br_version + '-' + br_release # ...и с релизом, если есть
                b = open(navigator_dir+'/brandings/my_brandings','a')
                b.write(new_br+'---'+new_br+'\n')
                b.close()
                if src_br == 'club_branding':  # если новый брендинг создаётся на основе клубного
                    subprocess.call('cp -r '+brandings_dir+'club_branding '+brandings_dir+new_br,shell=True) # копируем исходники клубного в каталог нового
                    subprocess.call('sed -i -e /Packager/d '+brandings_dir+'club_branding/branding/branding.spec && sed  "1,10c\\%define theme '+br_theme+'\\n%define Theme Club\\n%define codename Cheiron\\n%define brand '+br_n+'\\n%define Brand Alt Linux\\n\\nName: branding-%brand-%theme\\nVersion: '+br_version+'\\nRelease: '+br_release+'\\nPackager: '+ my_name+' <'+email+'>\\n" '+brandings_dir+'club_branding/branding/branding.spec > '+tmp_dir+'/spec',shell=True) # вписываем в спек данные нового брендинга
                else: # если новый брендинг создаётся на основе пользовательского, то делаем то же с ним
                    subprocess.call('cp -r '+brandings_dir+src_br+' '+brandings_dir+new_br,shell=True)
                    subprocess.call('sed  "1,10c\\%define theme '+br_theme+'\\n%define Theme Club\\n%define codename Cheiron\\n%define brand '+br_n+'\\n%define Brand Alt Linux\\n\\nName: branding-%brand-%theme\\nVersion: '+br_version+'\\nRelease: '+br_release+'\\nPackager: '+ my_name+' <'+email+'>\\n" '+brandings_dir+src_br+'/branding/branding.spec > '+tmp_dir+'/spec',shell=True)
                subprocess.call('cp -f '+tmp_dir+'/spec '+brandings_dir+new_br+'/branding/branding.spec',shell=True)
                open_f (n=br_dir1 + '/full_name',mode='w',tx=new_br_full)
                open_f (n=br_dir1 + '/branch',mode='w',tx=branch_var)
                brandings_pages()
           
        def br_choice(rb_name):  # выбор брендинга                  
            global src_br
            src_br = rb_name

        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/new_br.png',i=1,expl_loc='main_area.setGeometry(0,340,780,200)',inter_loc='inter.setGeometry(0,40,780,280)',t=u'Создание нового брендинга',pic_x=70)
        branch_var = 't7'
        open_f (n=navigator_dir+'/brandings/my_brandings',out='my_br',sl='.splitlines()')
        if my_br != []:
            open_f (n=tmp_dir+'/all_br',mode='w',tx=u'club_branding---Клубный брендинг\n'+'\n'.join(my_br)+'\n')  # добавляем к нему клубный брендинг
        else:
            open_f (n=tmp_dir+'/all_br',mode='w',tx=u'club_branding---Клубный брендинг')
        fr_all_brandings = R_But(x=40,y=60,h=220,w=250,filename=tmp_dir+'/all_br',parent=inter,func='br_choice',vis='line2[1]')        
        fr_branches = R_But(x=340,y=60,h=140,w=70,parent=inter,r_list=branches,func='active_branch',vis='line2[1]')
        t7_rb.setChecked(True)
        club_branding_rb.setChecked(True)
        src_br = 'club_branding'
        my_brandings_label = Label (parent=inter,x=60,y=40,tx=u'Базовые брендинги')
        branches_label = Label (parent=inter,x=340,y=40,tx=u'Бранчи')                     
        entry_name = Entry(x=500,y=55,width=200)
        entry_theme = Entry(x=500,y=105,width=200)
        entry_version = Entry(x=500,y=155,width=120)
        entry_release = Entry(x=640,y=155,width=60)
        entry_my_name = Entry(x=500,y=205,width=200)
        entry_email = Entry(x=500,y=255,width=200)
        br_name_label = Label (parent=inter,x=545,y=35,tx=u'Имя брендинга*')
        br_theme_label = Label (parent=inter,x=578,y=85,tx=u'Тема*')
        br_version_label = Label (parent=inter,x=540,y=135,tx=u'Версия*')
        br_release_label = Label (parent=inter,x=647,y=135,tx=u'Релиз*')
        br_my_name_label = Label (parent=inter,x=567,y=185,tx=u'Ваше имя')
        br_email_label = Label (parent=inter,x=520,y=235,tx=u'Ваш электронный адрес')             
        but_create_branding = But(parent=panel_action,com=create_branding,tx=u"Создать\nбрендинг")
        panel_action.resize(174,40)

# Удаление лишних брендингов
def delete_brandings():
    global fr_my_bra
    global list_True
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/br_edit.png',i=1,expl_loc='main_area.setGeometry(0,320,780,240)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Удаление лишних брендингов')

    def del_br():
        global project
        global list_True
        open_f (n=navigator_dir+'/brandings/main',out='brz1')
        open_f (n=navigator_dir+'/brandings/common_branding',out='brz2')
        if brz1+'---'+brz1 in list_True or brz2+'---'+brz2 in list_True:
            mes.new_mes(tx=u"Нельзя удалять\nдефолтный (для\nправки или сборки)\n брендинг",color='purple')
        else: 
            for x in list_True:    
                rmdir2 = subprocess.call('rm -rf '+brandings_dir+x.split('---')[0], shell=True) # удаляется каталог брендинга
            if  list_False != []:     
                open_f (n=navigator_dir+'/brandings/my_brandings',mode='w',tx='\n'.join(list_False)+'\n')  #  переписывается файл-список брендингов
            else:
                open_f (n=navigator_dir+'/brandings/my_brandings',mode='w',tx='')  #  если брендингов не осталось, конфиг очищается полностью  
            brandings_pages()                                                        
        
    but2 = But(parent=panel_action,com=del_br,tx=u"Удалить выбранные\nбрендинги")
    panel_action.resize(174,40)
    fr_my_bra = CheckBox_Group (lists=[(navigator_dir+'/brandings/my_brandings','False')],w=400, h=220) 

##### Редактирование выбранного брендинга #########
def branding(wb=0,demo_mode=0,demo_mode2=0):        
    global but_projects_hide    
    global var_headbands
    global mk_repo
    global br_is
    global work_branding
    global var_br_edit
    global insert_text
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/demo.png',t=u'Редактирование брендинга') 
    panel_action.hide()   
    br_is = 1   # индикатор для выбора между реальным редактированием брендинга и демо-режимом
    if demo_mode == 0 and demo_mode2 == 0 and var_br_edit != '' and var_br_edit != 'club_branding':  # если не отмечен какой-либо брендинг
        wb = 1    
    if wb == 0:   # редактировать брендинг по умолчанию или указанный пользователем
        open_f (n=navigator_dir+'/brandings/main',out='work_branding') # узнаём из конфига основной брендинг
        br_dir = brandings_dir+work_branding+'/branding' # каталог исходников брендинга
        br_dir0 = brandings_dir+work_branding # конфигурационный каталог брендинга        
        if work_branding == '':
            demo_mode = 1   # если нет активного брендинга, включаем демо-режим
        if demo_mode == 1:
            if demo_mode2 == 0:   # если демо-режим не включен ранее...
                subprocess.call('cp -rf '+''+brandings_dir+'club_branding '+tmp_dir, shell=True) # ...копируем клубный брендинг в tmpfs
            work_branding = 'club_branding'
            br_dir = tmp_dir+'/club_branding/branding'
            br_dir0 = tmp_dir+'/club_branding/'            
            but_new_branding = But(parent=panel_action,tx=u"Новый\nбрендинг",com=new_branding)
            br_is = 0
    else:
        work_branding = var_br_edit   # редактируем выбранный юзером брендинг
        br_dir = brandings_dir+work_branding+'/branding'
        br_dir0 = brandings_dir+work_branding
    if br_is == 1:
        open_f (n=brandings_dir+work_branding+'/full_name',out='work_br_full')
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/branding.png',t=u'Редактирование брендинга')
        if var_expls == 'True':
            insert_text = Label (parent=main_area,x=335,y=136,tx=work_branding)

    def gimp_inst():
        n = subprocess.Popen('rpm -q gimp', shell=True)   #  проверяем, установлен ли GIMP
        n.wait()
        if n.returncode !=0:
            gimp_required() 
            
    def grub():
        my_pic(title=u"Заставка загрузчика",ex="boot.png",f='grub.png',z=1,ret=grub)
    def boot_cd():
        my_pic(title=u"Заставка установочного диска",ex="cd.png",f='boot.png',z=1,ret=boot_cd)
    def loading():
        my_pic(title=u"Заставка при загрузке и отключении системы",ex="loading.png",f='background4x3.png')
    def greeting():
        my_pic(title=u"Приветствие при запуске ОС",ex="greeting.png",f='boot.jpg')
    def wallpaper():
        my_pic(title=u"Обои по умолчанию",ex="wallpaper.png",f='wallpaper.png')
    def installer():
        my_pic(title=u"Фон инсталлера",ex="installer.png",f='installer.png')                    
    def common_pic():
        global various_headbands
        various_headbands = 'False'
        my_pic(title=u'Редактирование всех заставок одновременно',ex="com_pic.png",f='background4x3.png',common=1)
        
    # Заставки дистрибутива.
    def my_pic(ex,title,f,z=0,ret='',common=0):
        global various_headbands
        subprocess.call('convert -resize 390x260  -extent 640x300 -gravity Center -background "#e9fbd5" '+br_dir+'/images/'+f+' '+tmp_dir+'/mini && montage -geometry +0+0 -background transparent -tile 1 '+pics_dir+'/explan/'+ex+' '+tmp_dir+'/mini '+tmp_dir+'/mini2',shell=True)  # создаём уменьшенные копии картинок для показа в программе
        page = Page(parent=root,z=tmp_dir+'/mini2',expl_loc='main_area.setGeometry(0,40,780,480)',t=title)

        def edit_pic():
            gimp_inst()
            g = subprocess.Popen('gimp '+br_dir+'/images/'+f+' &', shell=True)

        def examples():     # примеры заставок
            global cur_example
            page = Page(parent=root,z=tmp_dir+'/mini2',t=u'Примеры заставок')
            cur_example = 0

            def next_example():
                global cur_example
                but_prev.show()
                panel_action.resize(174,145)
                if cur_example == 2:
                    but_next.hide()
                    panel_action.resize(174,110) 
                cur_example= cur_example+1
                expl = Pic(im=pics_dir+'/examples/'+str(cur_example),x=60,y=20)

            def prev_example():
                global cur_example
                but_prev.hide()
                but_next.show()
                but_prev.show()
                panel_action.resize(174,145)
                if cur_example == 1:
                    but_prev.hide()
                    panel_action.resize(174,110)
                cur_example = cur_example-1
                expl = Pic(im=pics_dir+'/examples/'+str(cur_example),x=60,y=20)

            b1 = subprocess.Popen('ls '+pics_dir+'/examples > '+tmp_dir+'/boot_ex',shell=True)
            sleep(0.1)
            open_f (n=tmp_dir+'/boot_ex',out='b3',sl='.splitlines()')
            expl = Pic(im=pics_dir+"/examples/0")
            panel_action.hide()
            demo_real()
            but_boot = But(parent=panel_action,com=ret,tx=u"Заставки")
            but_next = But(parent=panel_action,com=next_example,tx=u"Следующий")
            but_prev = But(parent=panel_action,com=prev_example,tx=u"Предыдущий")
            but_prev.hide()
            panel_action_show()

        def ch_pic():            
            my_boot = QtGui.QFileDialog.getOpenFileName(root, u'Замена заставки',navigator_dir+'my_files') 
            if my_boot != '':
                c = subprocess.Popen('cp '+my_boot+' '+br_dir+'/images/'+f, shell=True)
                c.wait()
                if c.returncode == 0:
                    mes.new_mes(tx=u"Заставка обновлена")

        def change_all_pics():            
            if demo_mode == 0: # если не демо-режим...
                d = brandings_dir+work_branding+'/branding/images/' # ...работаем прямо с каталогом картинок брендинга 
            else:   # если демо-режим...
                d = tmp_dir+'/distronavigator/club_branding/branding/images/' # ...вычисляем каталог в tmpfs
                ch = subprocess.Popen('convert -sample 800x600 '+d+'background4x3.png '+d+'boot.png && convert -sample 800x600 '+d+'background4x3.png  '+d+'boot.jpg && rm -f '+d+'wallpaper.png '+d+'grub.png && cp -f '+d+'background4x3.png  '+d+'wallpaper.png && cp -f '+d+'boot.png  '+d+'grub.png',shell=True)  # применяем указанную юзером картинку ко всем заставкам
                ch2 = ch.wait()
                if ch2 == 0:
                    mes.new_mes(tx=u"Заставка обновлена")
                else :
                    mes.new_mes(tx=u"Заставку обновить\nне удалось",color='red')
          
        panel_action.hide()                        
        demo_real()
        if various_headbands == True:
            but0 = But(parent=panel_action,com=several_pic,tx=u"Все заставки")
        but1 = But(parent=panel_action,com=edit_pic,tx=u"Править картинку")
        but2 = But(parent=panel_action,com=ch_pic,tx=u"Сменить картинку")
        if z == 1:
            but3 = But(parent=panel_action,com=examples,tx=u"Примеры")
        if common == 1:
            but = But(parent=panel_action,com=change_all_pics,tx=u"Применить\nизменения")
        panel_action_show()    
            
    # Слайд-шоу инсталлера
    def slides():
        sl1 = ''+brandings_dir+'club_branding/branding/slideshow/slide1.png'
        if subprocess.os.path.exists(br_dir+'/slideshow/slide1.png'): # проверяем, есть ли slide1 в активном брендинге...
            sl1 = br_dir+'/slideshow/slide1.png'
        subprocess.call('montage -geometry +0+0 -background transparent -tile 1 '+pics_dir+'/explan/slideshow.png ' +sl1+ ' ' +tmp_dir+'/mini2',shell=True)    # ...показываем его или slide1 из клубного брендинга
        page = Page(parent=root,z=tmp_dir+'/mini2',t=u'Слайд-шоу')
        def show_slides():
            global cur_slide              
            
            def next_slide(event):
                global cur_slide
                but_prev.show()
                panel_action.resize(174,218)                   
                if cur_slide == len(nums)-2:
                    but_next.hide()
                    panel_action.resize(174,178)                 
                cur_slide = cur_slide+1
                expl = Pic(im=tmp_dir+'/slides/'+str(nums[cur_slide]),x=0,y=30)

            def prev_slide(event):
                global cur_slide
                but_prev.hide()
                but_next.show()
                but_prev.show()
                if cur_slide == 1:
                    but_prev.hide()
                    panel_action.resize(174,178)
                if cur_slide == len(nums)-1:
                    panel_action.resize(174,218)                    
                cur_slide = cur_slide-1
                expl = Pic(im=tmp_dir+'/slides/'+str(nums[cur_slide]),x=0,y=30)

            def edit_slide():
                global cur_slide
                gimp_inst()
                subprocess.call('gimp '+br_dir+'/slideshow/slide'+str(nums[cur_slide])+'.png &', shell=True)

            def del_slide():
                subprocess.call('rm -f '+br_dir+'/slideshow/slide'+str(nums[cur_slide])+'.png &', shell=True)
                mes.new_mes(tx=u"Слайд удалён")

            cur_slide = 0 
            sls1 = subprocess.Popen('ls '+br_dir+'/slideshow > '+tmp_dir+'/sls',shell=True)
            sleep(0.1)
            open_f (n=tmp_dir+'/sls',out='sls3',sl='.splitlines()')
            if sls3 == []:
                mes.new_mes(tx=u"Слайдов нет",color='purple')
            else:
                subprocess.call('mkdir -p '+tmp_dir+'/slides', shell=True)
                
                nums = []
                for x in sls3:
                    b = x[5:7].replace('.','')
                    if b[0] == '0':
                        b = b.replace('0','')
                    nums.append(int(b))
                    subprocess.call('ln -sf '+br_dir+'/slideshow/'+x+' '+tmp_dir+'/slides/'+b,shell=True)
                nums.sort()
                
                page = Page(parent=root,z=tmp_dir+'/slides/'+str(nums[0]),t=u'Просмотр слайд-шоу и правка слайдов',pic_x=60)
                panel_action.hide()
                demo_real()
                but_slides = But(parent=panel_action,com=slides,tx=u"Все слайды")
                but_del = But(parent=panel_action,com=del_slide,tx=u"Удалить слайд")
                but_edit = But(parent=panel_action,com=edit_slide,tx=u"Править слайд")                
                but_next = But(parent=panel_action,com=next_slide,tx=u"Следующий")
                but_next.setShortcut("x")
                but_prev = But(parent=panel_action,com=prev_slide,tx=u"Предыдущий")
                but_prev.setShortcut("z")              
                but_prev.hide()
                panel_action_show()

        def add_slides():
            my_slides = QtGui.QFileDialog.getOpenFileNames(root, u'Добавление своих слайдов',navigator_dir+'my_files')            
            subprocess.call('cp '+' '.join(my_slides)+' '+br_dir+'/slideshow',shell=True)
            if my_slides != [] and my_slides != '':
                mes.new_mes(tx=u"Слайды\nдобавлены")
        def del_slides():
            subprocess.call('rm -rf '+br_dir+'/slideshow/*', shell=True)
            mes.new_mes(tx=u"Слайды удалены")

        panel_action.hide()
        demo_real()
        but_add = But(parent=panel_action,com=add_slides,tx=u"Добавить\nслайды")
        but_del = But(parent=panel_action,com=del_slides,tx=u"Удалить все\nслайды")
        but_show = But(parent=panel_action,com=show_slides,tx=u"Просмотр слайд-шоу")  
        panel_action_show()        
            
    def headbands():        
        open_f (n=navigator_dir+'/settings/headbands',out='o')
        if o == 'True':
            choice_headbands()
        else:
            open_f (n=navigator_dir+'/brandings/headbands',out='o')    
            if o == 'False':
                common_pic()
            else:
                several_pic() 
            
    # Выбираем, использовать ли общую заставку или различные
    def choice_headbands():
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/hbs2.png',t=u'Общая заставка или разные?')
        def one_pic():
            global var_headbands
            open_f (n=navigator_dir+'/brandings/headbands',mode='w',tx='False')
            open_f (n=navigator_dir+'/settings/headbands',mode='w',tx='False')
            var_headbands = 'False'
            common_pic()
        def various_pic():
            global var_headbands
            open_f (n=navigator_dir+'/brandings/headbands',mode='w',tx='True')
            open_f (n=navigator_dir+'/settings/headbands',mode='w',tx='False')
            var_headbands = 'False'
            several_pic()            
        but1 = But(parent=panel_action,com=common_pic,tx=u"Использовать\nобщую заставку")
        but2 = But(parent=panel_action,com=several_pic,tx=u"Использовать\nразные заставки")
        but3 = But(parent=panel_action,com=one_pic,tx=u"Всегда использовать\nобщую заставку")
        but4 = But(parent=panel_action,com=various_pic,tx=u"Всегда использовать\nразные заставки")
        panel_action.resize(174,144)

    def several_pic():  # если используются разные заставки
        global various_headbands
        various_headbands = True
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/hbs.png',t=u'Выбор заставки для редактирования')
        panel_action.hide()
        demo_real()
        but1 = But(parent=panel_action,com=boot_cd,tx=u"Заставка\nустановочного диска")
        but2 = But(parent=panel_action,com=installer,tx=u"Фон инсталлера")
        but3 = But(parent=panel_action,com=grub,tx=u"Фон\nзагрузчика")
        but4 = But(parent=panel_action,com=greeting,tx=u"Приветствие")
        but5 = But(parent=panel_action,com=loading,tx=u"Заставка при загрузке\nи отключении системы")
        but6 = But(parent=panel_action,com=wallpaper,tx=u"Обои")
        panel_action_show()

    def gimp_required():
        mes.new_mes(tx=u"Необходимо установить\nпрограмму GIMP",color='purple')                           
              
    def installer():
        my_pic(title=u"Фон инсталлера",ex="installer.png",f='installer.png')
               
    def info():
        def write_info():
            open_f (n='/usr/share/distronavigator/main/info',out='t2') # открываем шаблон (html)
            s1=unicode(text1.toPlainText())
            s2=unicode(text2.toPlainText())
            s3=unicode(text3.toPlainText())            
            t5 = t2.replace('x1',s1).replace('x2',s2).replace('x3',s3) # вставляем туда то, что написал юзер
            if demo_mode == 1:
                open_f (n=tmp_dir+'/club_branding/branding/notes/release-notes.ru.html.in',mode='w',tx=t5)
            else:
                open_f (n=brandings_dir+work_branding+'/branding/notes/release-notes.ru.html.in',mode='w',tx=t5)
            info()
            mes.new_mes(tx=u'Новый вариант\nинформации о\nдистрибутиве записан')

        def example_info():
            page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/info2.png',t=u'Пример информации о дистрибутиве',i=1,expl_loc='main_area.setGeometry(0,440,780,100)',inter_loc='inter.setGeometry(0,40,780,380)')
            panel_action.hide()
            tw = Tx_wind (source=navigator_dir+'/brandings/info',out='f2',h=350,w=600,x=30,y=20,font='Arial 11',dis=1,butt='')
            demo_real()
            but1 = But(parent=panel_action,com=info,tx=u"Вернуться к своему\nдистрибутиву")
            panel_action.resize(174,75)           
            panel_action_show()   
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/info.png',t=u'Информация о дистрибутиве',i=1,expl_loc='main_area.setGeometry(0,440,780,100)',inter_loc='inter.setGeometry(0,40,780,380)')
        open_f (n=br_dir0+'/branding/notes/release-notes.ru.html.in',out='g')
        y = g.split('<a name = m>')
        text1 = QTextEdit (parent=inter,plainText=y[1])
        text2 = QTextEdit (parent=inter,plainText=y[3])
        text3 = QTextEdit (parent=inter,plainText=y[5])
        text1.setGeometry(30,30,650,40)
        text2.setGeometry(30,100,650,200)
        text3.setGeometry(30,330,650,40)
        text1.show()
        text2.show()
        text3.show()
        label_1 = Label(parent=inter,x=250,y=10,tx=u'Вступление')
        label_1 = Label(parent=inter,x=265,y=80,tx=u'Текст')
        label_1 = Label(parent=inter,x=260,y=310,tx=u'Подпись')
        panel_action.hide()
        demo_real()
        but1 = But(parent=panel_action,com=write_info,tx=u"Записать\nновый вариант")
        but2 = But(parent=panel_action,com=example_info,tx=u"Пример информации\nо дистрибутиве")
        panel_action_show()        
        
    # Очистка хашерницы
    def hasher_clean():
        q = open(navigator_dir+'/settings/tmpfs_b')
        open_f (n=navigator_dir+'/settings/tmpfs_b',out='q2')
        if q2 == 'True':
            hasher_path = tmp_dir
        else:
            hasher_path = navigator_dir
        u = subprocess.Popen('hsh '+hasher_path+'/hasher --cleanup-only',shell=True)
        u.wait()
        if u.returncode != 0:
            mes.new_mes(tx=u"Очистка не удалась",color='red')
        else:
            mes.new_mes(tx=u"Очистка успешно\nзавершена")
            
    def demo_real():  # привязываем кнопку к разным командам в зависимости от того, включен ли демо-режим
        if br_is == 1:
            but_br = But(parent=panel_action,com=branding,tx=u"Весь брендинг")
        if br_is == 0:
            but_br = But(parent=panel_action,com=demo_re,tx=u"Весь брендинг")               
                
    ### Заново собираем  пакеты брендинга и кладём их в свой репозиторий.
    def mk_branding():
      global make_b
      global make_d
      global br_thread
      global br_run
                
      open_f (n=brandings_dir+work_branding+'/branch',out='bran')
      nn = 1          
      open_f (n=navigator_dir+'/sources/my_repos-'+bran,out='t2',sl='.splitlines()')  #  смотрим, куда складывать готовые пакеты брендинга
      for x in t2:
          if '#my_repo' in x:
              rep2 = x.replace('rpm file:','').replace(' #my_repo','').split(' ')  # находим первый в списке локальный дополнительный репозиторий
              break   
      open_f (n=navigator_dir+'/main/branch',mode='w',tx=bran)
      for i in t2:
          if 'rpm' not in i:  # проверка, не забыл ли юзер указать репозитории для данного бранча
                nn = 0
      if make_b == True:
          mes.new_mes(tx=u"Нельзя начинать\nновую сборку пакетов,\nне завершив прежнюю",color='purple') 
      elif make_d == True:
          mes.new_mes(tx=u"Нельзя одновременно\nсобирать дистрибутив\nи пакеты брендинга",color='purple')
      elif nn == 0:
          all_repos()          
          top_params.re_color()
          mes.new_mes(tx=u'Похоже, не указаны\nрепозитории.\nПереходим туда,\nгде их можно указать',color='purple')
      else:
            # Создание нового потока
            class Thread_branding(QObject):
                def run(self):
                    global break_branding
                    global hasher_run
                    global break_by_user
                    global next_command
                    def break_branding():  # приказ прервать сборку
                        global break_by_user
                        global u
                        global hasher_run
                        break_by_user  = True                        
                        if hasher_run == True:
                            subprocess.call('killall hsh hsh-install hasher-priv',shell=True)       # прерываем сборку
                        else:
                            u.terminate()      # прерывание сборки 

                    def ex(com,mes_err,signal):  # выполняем команды конфигурирования, сборки, очистки
                        global break_by_user 
                        global u
                        global next_command 
                        self.emit(QtCore.SIGNAL('valueChanged(QString)'),signal)   
                        u=subprocess.Popen(com, shell=True)      # выполняем команду 
                        u.wait()                        
                        if u.returncode != 0:  # если  завершилась неудачно...
                            next_command = False                  
                            if break_by_user == True:
                                self.emit(QtCore.SIGNAL('valueChanged(QString)'),'break_b')  # ...сообщаем о прерывании сборки
                            if break_by_user == False:
                                self.emit(QtCore.SIGNAL('valueChanged(QString)'),mes_err)  # ...сообщаем о неудаче сборки на таком-то этапе    
                        if u.returncode == 0 and mes_err=='genbasedir_err' and break_by_user == False:  # если это была последняя команда и завершилась успешно   # ИСПРАВИТЬ!!!!!!
                            self.emit(QtCore.SIGNAL('valueChanged(QString)'),'branding_ok')  # ...сообщаем, что всё готово                          

                    break_by_user = False                     # индикатор, показывающий, завершилась ли сборка сама или была прервана пользователем
                    hasher_run = False
                    next_command = True            
                    subprocess.os.chdir(brandings_dir+work_branding)   # переходим в каталог исходников брендинга
                    self.connect(self,QtCore.SIGNAL('valueChanged(QString)'),observer.ob)                   
                    ex(com ='tar -cf branding.tar branding', mes_err='tar_err',signal='tar_start')      #  упаковка исходников в архив
                    if next_command == True:
                        ex(com = 'rpm -ts  branding.tar',mes_err='srpmbuild_err',signal='srpmbuild_start')      #  создание srpm
                    if next_command == True:    
                        hasher_run = True
                        ex(com = 'hsh '+hasher_dir+'/hasher --no-sisyphus-check --lazy-cleanup '+' --target='+rep2[1]+' --repo='+rep2[0]+' '+apt_conf+' '+home_dir+'/RPM/SRPMS/branding-'+work_br_full+'.src.rpm',mes_err='rpmbuild_err',signal='rpmbuild_start')     #  сборка rpm-пакетов в хашернице
                        hasher_run = False
                    if next_command == True:    
                        ex(com = 'genbasedir --topdir='+rep2[0]+' '+rep2[1]+' '+rep2[2],mes_err='genbasedir_err',signal='genbasedir_start')  #  обновление базы данных личного репозитория
                    
            
            open_f (n=brandings_dir+work_branding+'/full_name',out='work_br_full')
            open_f (n=navigator_dir+'/sources/local_net-'+bran,out='nl2')  #  сетевые или локальные репозитории этого бранча задействованы
            open_f (n=navigator_dir+'/sources/my_repos-'+bran,out='p2')
            if p2 == '':
                  mes.new_mes(tx=u"Похоже, не указаны\nрепозитории.\nПереходим туда,\nгде их можно указать",color='purple')
            else:
                apt_conf = ' --apt-config='+navigator_dir+'/sources/apt.conf-'+nl2+'-'+bran+' '
                open_f (n=navigator_dir+'/settings/tmpfs_b',out='th2')  #  использовать ли tmpfs для хашера
                if th2 == 'True':
                    subprocess.call('mkdir -p '+tmp_dir+'/hasher', shell=True)   #  создание хашерницы в tmpfs
                    hasher_dir = tmp_dir
                else:
                    hasher_dir = navigator_dir
                subprocess.call('rm -f '+tmp_dir+'/q1.sock '+tmp_dir+'/b.sock',shell=True)
                but_break_branding.show()
                panel_log.resize(174,40)
                panel_log.show()
                br_thread = QThread()
                br_run = Thread_branding()
                br_run.moveToThread(br_thread)
                br_thread.started.connect(br_run.run)                
                br_thread.start()     
    
    
    if work_branding == 'club_branding':
        what_branding.setText(u'Секция брендинга\nв демо-режиме')
    else:
        what_branding.setText(u'брендинг :\n'+work_branding)  #  указываем, какой брендинг в разработке
    what_branding.show()
        
    but1 = But(parent=panel_action,com=headbands,tx=u"Заставки",hint=u'Заставки, которые появляются при включении компьютера, загрузке системы и т.п')
    if various_headbands != 'True':
        but2 = But(parent=panel_action,com=installer,tx=u"Фон инсталлера",hint=u'Фоновая картинка, занимающая экран в течение всего процесса установки дистрибутива')
    but3 = But(parent=panel_action,com=slides,tx=u"Слайд-шоу",hint=u'Слайд-шоу, которое показывается во время установки дистрибутива')
    but4 = But(parent=panel_action,com=info,tx=u"Информация о\nдистрибутиве",hint=u'Сведения о дистрибутиве, которые вы считаете нужным донести до его пользователей.\n\n')
    if demo_mode == 0:  
        but5 = But(parent=panel_action,com=mk_branding,tx=u"Применить\n изменения",hint=u'Сделав такой брендинг, какой вам нравится, нажмите здесь. Процесс пересборки пакетов брендинга может занять порядка 10-20 минут, после чего появится соответствующее сообщение')
        but6 = But(parent=panel_action,com=hasher_clean,tx=u"Очистка\nсборочницы",hint=u'Очистка сборочницы, в которой создаются пакеты брендинга. Кнопка может потребоваться при  сбоях') 
    panel_action_show()
    
###### Параметры сборочной системы
def params():
    global inter
    global set_par
    global mp_mpd_default
    set_par = 'par'  # указание для класса Sett, что открыта страница параметров сборочницы, а не настроек программы.
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/params.png',i=1,expl_loc='main_area.setGeometry(0,220,780,310)',inter_loc='inter.setGeometry(30,70,780,150)',t=u'Сборочная система')
    inter.layout = QVBoxLayout(inter)
    
    def mp_mpd_default(rb_name):
        open_f(n=navigator_dir+'/main/mp_mpd',mode='w',tx=rb_name)
    
    def image_dir():
        s = open(navigator_dir+'/main/images_dir')
        i_dir = s.read().replace('--with-outdir=','')
        s.close()         
        if i_dir == '':
            i_dir = navigator_dir+'/my_images'
        im_dir = QFileDialog.getExistingDirectory(root, u'Каталог для готовых образов',navigator_dir+'/my_images')
        if im_dir != () and  im_dir != '':                
            open_f (n=navigator_dir+'/main/images_dir',mode='w',tx='--with-outdir='+im_dir)
        params()
                
    what_branding.setText('') 
    par_mp_mpd_choice = Sett (n='mp_mpd_choice',var=var_mp_mpd_choice,tx=u'Показывать кнопку переключения между сборочницами')
    par_tmpfs_b = Sett (n='tmpfs_b',var=var_tmpfs_b,tx=u'Собирать пакеты брендинга в tmpfs')
    par_tmpfs_d = Sett (n='tmpfs_d',var=var_tmpfs_d,tx=u'Собирать дистрибутивы в tmpfs')     
    par_nice = Sett (n='nice',var=var_nice,tx=u'Ограничить потребление ресурсов процессом сборки') 
    par_clean = Sett (n='clean',var=var_clean,tx=u'Очищать сборочницу после сборки дистрибутива')  
    fr_mp_mpd = R_But(x=485,y=50,h=80,w=210,r_list=['mp---mkimage-profiles','mpd---mkimage-profiles-desktop'],parent=inter,func='mp_mpd_default',vis='line2[1]',checked=navigator_dir+'/main/mp_mpd')
    mp_mpd_label = Label(parent=inter,x=460,y=30,tx=u'Сборочная система по умолчанию').adjustSize()      
    panel_action.hide()
    but_images = But(parent=panel_action,tx=u"Указать каталог\nдля образов",com=image_dir)
    but_repos = But(parent=panel_action,tx=u"Репозитории",com=all_repos)
    but_null = But(parent=panel_action,tx=u"Сброс",com=null,hint=u'Если запутались с профилями настолько, что ничего не работает, или же сборочница по какой-то причине поломалась, жмите сюда : сборочница восстановится в первоначальном виде. Если нажмёте случайно - есть возможность отмены.') 
    panel_action_show()
    log_restore()  
    
# Репозитории
def all_repos():
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/all_repos.png',t=u'Указание репозиториев')
    but_main_repos = But(parent=panel_action,tx=u"Обязательные\nрепозитории",com=main_repos)
    but_addon_repos = But(parent=panel_action,tx=u"Дополнительные\nрепозитории",com=addon_repos)    
    parent=panel_action.resize(174,75)    
    panel_action.show()
    
# Выбор репозиториев для каждого бранча
def main_repos():
    global branch_var
    global local_net_switch
    global branch_commit
            
    def main_r():
        repo_m = QFileDialog.getExistingDirectory(root, u'Местоположение зеркала основного репозитория',
                navigator_dir)
        if repo_m != '':
            entry_main_repo.setText(repo_m)  # адрес основного репозитория вписывается в соответствующее поле

    def club_r():
        repo_c = QFileDialog.getExistingDirectory(root, u'Местоположение зеркала клубного репозитория',navigator_dir)
        if repo_c != '':
            entry_club_repo.setText(repo_c)  # адрес клубного репозитория вписывается в соответствующее поле

    def mirror_com():  # обновляем файл со списком репозиториев
        global branch_var
        main_repo= str(entry_main_repo.text()) 
        club_repo= str(entry_club_repo.text())                    # получаем введённые юзером адреса репозиториев
        open_f (n=navigator_dir+'/sources/local_net-'+branch_var,out='n2') #  смотрим, локальные или сетевые репозитории у нас в нём задействованы
        if n2 == 'local':        
            subprocess.call ("sed -i -e '/#club_repo/crpm\ file:"+club_repo+" i686 hasher #club_repo' -e '/#main_repo_i/crpm\ file:"+main_repo+" i586 classic #main_repo_i' -e '/#main_repo_n/crpm\ file:"+main_repo+" noarch classic #main_repo_n' "+navigator_dir+"/sources/my_repos-"+branch_var,shell=True)  
        else:
            subprocess.call ("sed -i -e '/#club_repo/crpm\ "+club_repo+" i686 hasher #club_repo' -e '/#main_repo_i/crpm\ "+main_repo+" i586 classic #main_repo_i' -e '/#main_repo_n/crpm\ "+main_repo+" noarch classic #main_repo_n' "+navigator_dir+"/sources/my_repos-"+branch_var,shell=True)             # вписываем их в конфиг         
        mes.new_mes(tx=u'Список репозиториев\nобновлён')
        
    def repos_show():        
        open_f (n=navigator_dir+'/sources/my_repos-'+branch_var,out='p',sl='.splitlines()')  # смотрим файл со списком репозиториев
        m_repo = p[0].replace('rpm file:','').replace('rpm  ftp://','').replace(' i586 classic #main_repo_i','').replace('#main_repo_i','')  # вырезаем то, что отображать не надо
        c_repo = p[2].replace('rpm file:','').replace('rpm  ftp://','').replace(' i686 hasher #club_repo','').replace('#club_repo','')                                   
        entry_main_repo.setText(m_repo)  # вводим в них адреса репозиториев
        entry_club_repo.setText(c_repo)        

    def branch_commit(rb_name):  #  Переключение между бранчами для указания их репозиториев
        global branch_var       
        branch_var = rb_name
        open_f (n=navigator_dir+'/main/branch',mode='w',tx=rb_name)   #  отметка о том, с каким бранчем работаем
        open_f (n=navigator_dir+'/sources/local_net-'+rb_name,out='n2') #  смотрим, локальные или сетевые репозитории у нас в нём задействованы
        eval(n2+'_rb.setChecked(True)')
        repos_show()        
        
    def local_net_switch(rb_name):      # сетевые или локальные репозитории использовать
        global branch_var
        open_f (n=navigator_dir+'/sources/local_net-'+branch_var,mode='w',tx=rb_name) # записываем в конфиг
        if  rb_name == 'net':
            subprocess.call('cp -f '+navigator_dir+'/sources/my_repos-'+branch_var+' '+navigator_dir+'/sources/local_re-'+branch_var+' && cp -f '+navigator_dir+'/sources/net_re-'+branch_var+' '+navigator_dir+'/sources/my_repos-'+branch_var+'  > /dev/null 2>&1',shell=True)      # создаётся резервная копия локального варианта sources/my_repos*, после чего он заменяется файлом с указанием на сетевые репозитории указанного бранча
        if  rb_name == 'local':
            subprocess.call('cp -f '+navigator_dir+'/sources/my_repos-'+branch_var+' '+navigator_dir+'/sources/net_re-'+branch_var+' && cp -f '+navigator_dir+'/sources/local_re-'+branch_var+' '+navigator_dir+'/sources/my_repos-'+branch_var+' > /dev/null 2>&1',shell=True)   # создаётся резервная копия сетевого варианта sources/my_repos*, после чего он заменяется файлом с указанием на локальные зеркала указанного бранча
        repos_show()   

    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/main_repos.png',i=1,expl_loc='main_area.setGeometry(0,320,780,240)',inter_loc='inter.setGeometry(0,40,780,260)',t=u'Указание основных репозиториев')
    open_f (n=navigator_dir+'/main/branch',out='branch_var')  # репозитории какого бранча указываются
    fr_branches = R_But(x=35,y=60,h=140,w=70,parent=inter,r_list=branches,func='branch_commit',vis='line2[1]')
    eval(branch_var+'_rb.setChecked(True)')
    fr_loc_net = R_But(x=110,y=60,h=120,w=340,r_list=[u'local---Использовать локальное зеркало бранча',u'net---Использовать сетевые репозитории'],checked=navigator_dir+'/sources/local_net-'+branch_var,parent=inter,func='local_net_switch',vis='line2[1]')
    entry_main_repo = Entry(x=460,y=60,width=260)
    entry_club_repo = Entry(x=460,y=120,width=260)
    main_repo_label = Label(parent=inter,x=500,y=40,tx=u'Основной репозиторий')
    club_repo_label = Label(parent=inter,x=505,y=100,tx=u'Клубный репозиторий') 
    repos_show()         
    panel_action.hide()
    but_repos = But(parent=panel_action,tx=u"Все\nрепозитории",com=all_repos)
    but_main_repo = But(parent=panel_action,tx=u"Выбрать основной\nрепозиторий",com=main_r)
    but_club_repo= But(parent=panel_action,tx=u"Выбрать клубный\nрепозиторий",com=club_r)
    but_mirror_com = But(parent=panel_action,tx=u"Применить\nизменения",com=mirror_com)
    but_edit_repos_list= But(parent=panel_action,tx=u"Редактировать\nсписок репозиториев",com=edit_repos_list)    
    parent=panel_action.resize(174,180)
    panel_action_show()

       # Указание дополнительных репозиториев
def addon_repos():
    global my_other_repo
    global rbuttons_list
    global my_r
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/addon_repos.png',i=1,expl_loc='main_area.setGeometry(0,280,780,280)',inter_loc='inter.setGeometry(0,40,780,220)',t=u'Дополнительные репозитории')
        
    def search_repo():
        repo_path = QFileDialog.getExistingDirectory(root, u'Местоположение дополнительного репозитория',
                navigator_dir)
        if repo_path != '':
            entry_1.setText(repo_path)  # адрес основного репозитория вписывается в соответствующее поле  
                         
    def use_repo():         # задействовать существующий репозиторий
        if '://' not in entry_1.text():
            s = subprocess.os.path.exists (entry_1.text()+'/'+entry_2.text()+'/RPMS.'+entry_3.text())  # проверка наличия репозитория по указанному  адресу.....
            if s == False:
                mes.new_mes(tx=u"Репозиторий\nпо указанному адресу\nне обнаружен",color='purple')
            else:
                subprocess.call('sed -i "$ a rpm\ file:'+entry_1.text()+' '+entry_2.text()+' '+entry_3.text()+' #'+entry_1.text().replace('/','_')+'#my_repo" '+navigator_dir+'/sources/*_re*',shell=True)
                addon_repos()
        else:
            subprocess.call('sed -i "$ a rpm\ '+entry_1.text()+' '+entry_2.text()+' '+entry_3.text()+' #'+entry_1.text().replace('/','_')+'#my_repo" '+navigator_dir+'/sources/*_re*',shell=True)                                            
            addon_repos()            

          
    def new_repo():
        s = subprocess.os.path.exists (entry_1.text()+'/'+entry_2.text()+'/RPMS.'+entry_3.text())  # проверка наличия репозитория по указанному  адресу.....
        if s == True:
            mes.new_mes(tx=u"Такой репозиторий\nуже существует",color='purple')        
        else:
            n = subprocess.Popen ('mkdir -p '+entry_1.text()+'/'+entry_2.text()+'/RPMS.'+entry_3.text()+' '+entry_1.text()+'/SRPMS.'+entry_3.text()+' '+entry_1.text()+'/'+entry_2.text()+'/base && genbasedir --topdir='+entry_1.text()+' '+entry_2.text()+' '+entry_3.text(),shell=True)
            n.wait()
            if n.returncode != 0:
                mes.new_mes(tx=u"Создать репозиторий\nне удалось",color='red') 
            else:                
                subprocess.call('sed -i "$ a rpm\ file:'+entry_1.text()+' '+entry_2.text()+' '+entry_3.text()+' #'+entry_1.text().replace('/','_')+'#my_repo" '+navigator_dir+'/sources/*re*',shell=True)
                addon_repos()
         
    def my_other_repo(rb_name):
        global my_r
        my_r = rb_name
    
    def repo_off():
        if my_r == '':
            mes.new_mes(tx=u"Репозиторий\nне выбран",color='purple')
        else:
            subprocess.call('sed -i -e "/#'+my_r.replace('dott','.')+'#my_repo/d" '+navigator_dir+'/sources/*re*',shell=True)
            addon_repos()
                     
    open_f (navigator_dir+'/sources/my_repos-t7',out='rep2',sl='.splitlines()')
    my_repos_list = []
    list2 = [] 
    my_r = ''  # какой репозиторий отмечен для отключения
    for x in rep2:              
        if x.endswith('#my_repo'):
            my_repos_list.append (x.replace('rpm file:','').replace('#my_repo','').replace('rpm ftp://','').split(' '))   
    for x in my_repos_list:
        list2.append(x[0].replace('/','_').replace('.','dott')+'---'+x[0])
    fr_my_repos = R_But(x=35,y=60,h=190,w=420,parent=inter,r_list=list2,func='my_other_repo',vis="line2[1]")
    entry_1 = Entry(x=430,y=60,width=250)
    entry_2 = Entry(x=475,y=120,width=120)
    entry_3 = Entry(x=475,y=180,width=120)
    path_repo_label = Label(parent=inter,x=480,y=40,tx=u'Адрес репозитория')
    distro_repo_label = Label(parent=inter,x=495,y=100,tx=u'Дистрибутив')
    part_repo_label = Label(parent=inter,x=513,y=160,tx=u'Раздел')
    but_repos = But(parent=panel_action,tx=u"Все\nрепозитории",com=all_repos)
    but1 = But(parent=panel_action,com=search_repo,tx=u"Выбрать\nрепозиторий")                                 
    but1 = But(parent=panel_action,com=use_repo,tx=u"Подключить указанный\nрепозиторий")
    but1 = But(parent=panel_action,com=new_repo,tx=u"Создать новый\nрепозиторий")
    but1 = But(parent=panel_action,com=repo_off,tx=u"Отключить отмеченный\nрепозиторий")       
    parent=panel_action.resize(174,180)     
    
def mk_repo_0(): 
    mk_repo(my_r='')  
    
def edit_repos_list():  # правка списка репозиториев вручную        
    global branch_var
    global insert_text
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/edit_repos_list.png',i=1,expl_loc='main_area.setGeometry(0,320,780,230)',inter_loc='inter.setGeometry(0,40,780,270)',t=u'Ручная правка списка репозиториев')
    insert_text = Label (parent=main_area,x=163,y=97,tx=branch_var+'                     '+navigator_dir+'/sources/my_repos-'+branch_var)
    tw = Tx_wind (source=navigator_dir+'/sources/my_repos-'+branch_var,out='r_list',h=212,w=695,x=20,y=40,font='Arial 12',del_end=True,mess=u'Список репозиториев\nобновлён')
    but_main_r = But(parent=panel_action,com=main_repos,tx=u"Назад")
    panel_action.resize(174,75)     

# Восстановление сборочницы в первоначальном виде
def null():
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/empty_'+mp_mpd+'.png',t=u'Сброс')
    def restor_part():
        n = subprocess.Popen('tar xf /usr/share/distronavigator/mpd.tar.gz -C '+tmp_dir+' && cp -rf '+build_dir+'/Makefile.in '+tmp_dir+'/mpd && cp -rf '+build_dir+'/configure.ac '+tmp_dir+'/mpd && cp -rf '+build_dir+'/profiles/pkg/lists/*  '+tmp_dir+'/mpd/profiles/pkg/lists  &&  cp -rf '+build_dir+'/profiles/pkg/groups/*  '+tmp_dir+'/mpd/profiles/pkg/groups  &&     rm -rf '+build_dir+' && mv  '+tmp_dir+'/mpd '+navigator_dir, shell=True)
        n.wait()   # перенос проектов из старой сборочницу в новую и удаление старой
        if n.returncode == 0:
            mes.new_mes(tx=u"Сборочная система -\nв первоначальном виде.\nВаши проекты \nсохранены")
        else:
            mes.new_mes(tx=u"Не удалось вернуть\nсборочную систему в\nпервоначальное состояние",color='red')

    but1 = But(parent=panel_action,com=restor,tx=u"Начать всё с нуля",hint=u'Восстановить сборочную систему с нуля, с удалением всех проектов.',evil=True)
    but2 = But(parent=panel_action,com=restor_part,tx=u"Начать с нуля,\nсохранив проекты",hint=u'Восстановить сборочную систему с нуля, но с сохранением ранее созданных проектов.',evil=True)
    but3 = But(parent=panel_action,tx=u"Отмена",com=params,hint=u'Если нажали "Сброс" случайно или не подумав, жмите здесь.')
    panel_action.resize(174,110)
         
#### Настройки программы
def set_gui():
    global inter
    global fr_settings
    global var_expls
    global set_par
    set_par = 'set' # указание для класса Sett, что открыта страница настроек программы, а не параметров сборочницы. 
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/set.png',i=1,expl_loc='main_area.setGeometry(0,250,780,300)',inter_loc='inter.setGeometry(30,80,780,160)',t=u'Настройки программы')
    panel_action.hide()
    inter.layout = QVBoxLayout(inter)
    what_branding.setText('')                                       
    ch_baseprojects = Sett (n='baseprojects',var=var_baseprojects,tx=u'Возможность сборки не только своих, но и базовых дистрибутивов')
    ch_brandings_use = Sett (n='brandings_use',var=var_brandings_use,tx=u'Показывать страницу выбора брендингов для использования')
    ch_brandings_edit = Sett (n='brandings_edit',var=var_brandings_edit,tx=u'Показывать страницу выбора брендингов для редактирования')
    ch_headbands = Sett (n='headbands',var=var_headbands,tx=u'Предлагать выбор между общей заставкой и разными')
    ch_expls = Sett (n='expls',var=var_expls,tx=u'Показывать пояснения')
    ch_popup = Sett (n='popup',var=var_popup,tx=u'Показывать подсказки к кнопкам')
    ch_music = Sett (n='music',var=var_music,tx=u'Звуковое оповещение о завершении сборки')
    log_restore()     
   
# Главная страница
def main_page():

    def developer():
        global browser
        subprocess.call(browser+' http://forum.russ2.com/index.php?showtopic=3500 &', shell=True)

    def forum():
        global browser
        subprocess.call(browser+' http://forum.russ2.com/index.php?showforum=124 &', shell=True)

    def quickstart():
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/begin.png',t=u'С чего начать')
        but_br = But(parent=panel_action,com=man_branding,tx=u"Создание\nбрендинга")
        but_d = But(parent=panel_action,com=man_distro,tx=u"Создание\nдистрибутива")
        but_adv = But(parent=panel_action,com=advices,tx=u"Советы по работе\n с программой")
        panel_action.resize(174,114)
        
    def man_branding():
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/help_br.png',t=u'Кратко о создании брендинга')
        but_1 = But(parent=panel_action,com=quickstart,tx=u"Все\nинструкции")
        panel_action.resize(174,40)

    def man_distro():
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/help_distro.png',t=u'Кратко о создании дистрибутива')
        but_1 = But(parent=panel_action,com=quickstart,tx=u"Все\nинструкции")
        panel_action.resize(174,40)
        
    def advices():
        page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/help.png',t=u'Советы по работе с программой')
        but_1 = But(parent=panel_action,com=quickstart,tx=u"Все\nинструкции")
        panel_action.resize(174,40)
        
    page = Page(parent=root,z='/usr/share/distronavigator/pics/explan/mainpage.png',t=u'Навигатор для дебрей альтовского дистростроя',pic_y=10)   
    what_branding.setText('')
    but_forum = But(parent=panel_action,tx=u"Наш\nфорум",com=forum)
    but_developer = But(parent=panel_action,tx=u"Обсуждение\nпрограммы",com=developer)
    but_quickstart = But(parent=panel_action,tx=u"С чего\nначать?",com=quickstart)     
    panel_action.resize(174,109)
    panel_action.show()
    top_but_equal()
    button_re.hide()  # скрываем кнопку возврата на главную страницу
    log_restore()     

##################### Основа программы #####################

# Настройка программы соответственно конфигам
for z in ['set','params']:
    open_f (n=navigator_dir+'/settings/list_'+z,out='b',sl='.splitlines()')
    for x in b:                           # ...для каждой из них ....
        exec eval('''"var_"+x+" = ''"''') in globals(),locals()          # ...  создаём свою переменную.....
        open_f (n=navigator_dir+'/settings/'+x,out='y')
        exec eval("'var_'+x+'=y'")in globals(), locals()  # .... и записываем в неё из конфига статус опции

open_f(n=navigator_dir+'/main/src_branding',out='src_branding_is')
app = QApplication(sys.argv)
root = QMainWindow() #  создаём окно программы
root.move(50,80)  #  задаём его размеры и расположение на экране
root.setFixedSize(960,560)
icon_pic = QPixmap()   # показываем пояснения, если велено
icon_pic.load('/usr/share/distronavigator/distronavigator.png')
icon = QIcon(icon_pic)
app.setWindowIcon(icon)
main_area = QLabel(root)  #  область пояснительного текста и картинок
main_area.setGeometry(0,40,780,520)               
top_box = QGroupBox(parent=root)  #  фрейм для верхних кнопок
top_box.setGeometry(2, 0, 760, 30) 
top_box.layout = QHBoxLayout(top_box)
top_box.layout.setSpacing(4)  #  расстояние между верхними кнопками
top_box.layout.setContentsMargins(2,2,2,2)
top_projects = Top(com=projects,tx=u'Проекты') 
top_pkglists = Top(com=pkglists,tx=u'Состав сборки') 
top_branding = Top(com=brandings_pages,tx=u'Оформление') 
top_params = Top(com=params,tx=u'Сборочная система') 
top_set_gui = Top(com=set_gui,tx=u'Настройки программы')                                            
main_area.show()
root.show()
button_re = QPushButton(u"На главную\nстраницу",parent=root)  # кнопка возврата на главную страницу (изначально скрыта)
button_re.setGeometry(787, 450, 168, 33)
button_re.clicked.connect(main_page)
panel_action = QGroupBox(parent=root)  #  панель действий
panel_action.move(785, 95)
panel_action.layout = QVBoxLayout(panel_action)
panel_action.layout.setSpacing(1)
panel_action.layout.setContentsMargins(2,2,2,2)
panel_action.show()
panel_log = QGroupBox(parent=root)     # панель кнопок, требующихся во время сборки
panel_log.move(785,350)
panel_log.layout = QVBoxLayout(panel_log)
panel_log.layout.setSpacing(1)
panel_log.layout.setContentsMargins(2,2,2,2)                                
what_project = QLabel(root)   # показ того, какой проект в разработке
what_project.show() 
what_project.setGeometry(785,0,180,60)
what_branding = QLabel(root)  # показ того, какой брендинг в разработке
what_branding.setGeometry(785,50,180,30)
what_stat = QLabel(root)  # показ хода сборки
what_stat.setGeometry(785,500,160,60)
what_stat.show()
mes = Message()  # сообщения от программы (изначально скрыто, показывается лишь при надобности)    
but_log = But(parent=panel_log,tx=u"Журнал",com=log)  # кнопка показа журнала сборки
but_log_re = But(parent=panel_log,tx=u"Обновить\nжурнал",com=log_re)
but_log_report = But(parent=panel_log,tx=u"Отчёт о\nсборке",com=log_report)
but_break_mk_distro = But (parent=panel_log,com=break_mk_distro2,tx=u"Прервать\nсборку",evil=True)
but_break_branding = But (parent=panel_log,com=break_branding2,tx=u"Прервать\nсборку",evil=True)
but_break_mk_distro.hide()
but_break_branding.hide()
but_log.hide()
browser_ch()
brand = ''  # выбранный юзером брендинг
choice_project = '' # указывает, пользовательский или базовый дистрибутив будет собираться
observer = Observ()  # наблюдение за процессом сборки
open_f (n=navigator_dir+'/main/mp_mpd',out='mp_mpd')
but_mp_mpd = QPushButton(u"",parent=root,text=mp_mpd)  # кнопка переключения сборочниц
but_mp_mpd.setGeometry(910, 525, 48, 33)
but_mp_mpd.clicked.connect(mp_mpd_switch)
mp_mpd_choice() 
# Настройка программы под проект, который активен по умолчанию
open_f (n=conf_dir+'/default_project',out='default_project')  # определяем проект по умолчанию
project = 'none'   # заглушка на случай отсутствия такового
d = subprocess.os.path.exists(conf_dir+'/projects/'+default_project)  # проверяем его наличие 
if d == True:
    project = default_project # устанавливаем проект по умолчанию
hasher()  # проверяем право юзера использовать hasher
if var_mp_mpd_choice == 'True':
    but_mp_mpd.show()
main_page()
sys.exit(app.exec_())

