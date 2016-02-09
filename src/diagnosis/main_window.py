import subprocess, sys, logging, servlet, random, time, os, signal
from diagnosis_service import DiagnosisService

from PyQt4 import QtCore, QtGui

PEER_PATH = './peer/p2psearch.py'
DOT_EXEC_PATH = 'neato'
TMP_DOT_FILE = '.tmp.dot'
TMP_IMAGE_FILE = '.tmp.png'

def star_topology(n, diagnosis=None):
    # center
    center_port = random.randint(10000, 65000)
    run_peer(dest_port=center_port, diagnosis=('localhost', 12000))

    time.sleep(1)
    procs = []

    for _ in range(0, n):
        procs.append(run_peer(initial_peers=[('localhost', center_port)],
                              diagnosis=diagnosis))
        time.sleep(1)



class ServletListWidgetItem(QtGui.QListWidgetItem):
    def __init__(self, this_servlet):
        QtGui.QListWidgetItem.__init__(self)

        if type(this_servlet) is not servlet.Servlet:
            raise TypeError('excpected Servlet, got %s'
                            % type(this_servlet))

        self.__servlet = this_servlet

        self.setText(str(self.__servlet))

        MULT = 255
        
        color = QtGui.QColor()
        color.setHsv(MULT * self.__servlet.color['h'],
                     MULT * self.__servlet.color['s'],
                     MULT * self.__servlet.color['v'])

        self.setBackground(color)



    def get_servlet(self):
        return self.__servlet

    def __lt__(self, other):
        return self.text() < other.text()


def run_peer(dest_port=None, initial_peers=None,
             diagnosis=None, proxy_port=None):
    cmd = [PEER_PATH]

    
    if proxy_port is None:
        proxy_port = random.randint(10000, 65000)

    cmd.extend(['--proxy-port', str(proxy_port)])

    if dest_port:
        cmd.extend(['--dest-port', str(dest_port)])

    if initial_peers:
        pairs = ('%s:%d' % (ip, port) for ip, port in initial_peers)
        cmd.append('--peers')
        cmd.extend(pairs)

    if diagnosis:
        cmd.extend(['--diagnosis', '%s:%d' % diagnosis])    

    proc = subprocess.Popen(cmd, 
                            stdin=None, stdout=sys.stdout,
                            stderr=sys.stderr, close_fds=True)

    return proc


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.__diagnosis_service = DiagnosisService()

        logging.info('port for diagnosis service is %d'
                     % self.__diagnosis_service.get_port())

        self.__diagnosis_service.new_servlet.connect(self.got_new_servlet)

        self.__diagnosis_service.disconnected_servlet.connect(
            self.disconnected_servlet_callback)

        self.__diagnosis_service.start()

        self.__init_ui()


    def disconnected_servlet_callback(self, disconnected_servlet):
        if type(disconnected_servlet) is not servlet.Servlet:
            raise TypeError('expected a Servlet, got a %s'
                            % type(disconnected_servlet))

        self._update_callback()


    def got_new_servlet(self, new_servlet):
        logging.info('got a new servlet')
        self._update_callback()

    def _new_servlet_callback(self):

        diagnosis_arg = ('localhost', self.__diagnosis_service.get_port())

        run_peer(diagnosis=diagnosis_arg)


    def _update_callback(self):

        self.__diagnosis_service.update_all()

        self.__servlets_list.clear()

        for crnt_servlet in self.__diagnosis_service.get_servlets():

            crnt_servlet_item = ServletListWidgetItem(crnt_servlet)

            self.__servlets_list.addItem(crnt_servlet_item)

        with open(TMP_DOT_FILE, 'w') as tmp_file:
                
            tmp_file.write(self.__diagnosis_service.export_to_dot())

        # dot -Tpng .tmp.dot -o test.png
        args = [
            DOT_EXEC_PATH,
            '-Tpng',
            TMP_DOT_FILE,
            '-o',
            TMP_IMAGE_FILE
        ]

        retcode = subprocess.call(args)

        logging.debug('return code of %s: %s'
                      % (DOT_EXEC_PATH, retcode))
        if os.path.exists(TMP_IMAGE_FILE):
            self.__scene.clear()
            pic = QtGui.QPixmap(TMP_IMAGE_FILE)
            self.__scene.addPixmap(pic)
        else:
            logging.error('unable to find %s' % TMP_IMAGE_FILE)
                        


    def _servlets_list_selection_changed_callback(self):
        self.__detailsList.clear()

        crnt_servlet = self.__servlets_list.selectedItems()[0].get_servlet()

        self.__detailsList.addItem('port: %s'
                                   % crnt_servlet.get_dest_port())

        self.__detailsList.addItem('created at: %s'
                                   % crnt_servlet.get_created_at().strftime("%H:%M:%S %Z"))

        self.__detailsList.addItem('pid: %d'
                                   % crnt_servlet.pid)

        for crnt_peer in crnt_servlet.get_peers():
            self.__detailsList.addItem('%s:%d'
                                       % (crnt_peer['ip'], crnt_peer['port']))
                                       

    def _new_servlet_with_given_entry_point(self, entry_point):
        if type(entry_point) is not servlet.Servlet:
            raise TypeError('expected a Servlet')


        logging.info(('about to create a new peer that uses ' +
                      '%s as its entry point') % entry_point)

        initial_peers = [
            (entry_point.get_ip(), entry_point.get_dest_port())
        ]
        

        run_peer(initial_peers=initial_peers,
                 diagnosis=('localhost', self.__diagnosis_service.get_port()))

    def _handle_servlet_context(self, pos):
        item = self.__servlets_list.itemAt(pos)
        if item is not None:
            selected_servlet = item.get_servlet()
            menu = QtGui.QMenu("Context Menu", self)
            menu.addAction('Use as entry point for new peer',
                           lambda: self._new_servlet_with_given_entry_point(selected_servlet))
            menu.addAction('kill process',
                           lambda: self._kill_process_of_servlet(selected_servlet))
            ret = menu.exec_(self.__servlets_list.mapToGlobal(pos))


    def _kill_process_of_servlet(self, servl):
        os.kill(servl.pid, signal.SIGKILL)


    def __init_ui(self):

        grid = QtGui.QGridLayout()

        grid.setColumnStretch(1,1)

        widget = QtGui.QWidget(self)

        widget.setLayout(grid)

        self.setCentralWidget(widget)

        # list of servlets

        self.__servlets_list = QtGui.QListWidget()

        self.__servlets_list.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu)

        self.__servlets_list.customContextMenuRequested.connect(
            self._handle_servlet_context)

        self.__servlets_list.itemClicked.connect(
            self._servlets_list_selection_changed_callback)

        widget.layout().addWidget(self.__servlets_list, 0, 0, 1, 1)

        # graph

        self.__grview = QtGui.QGraphicsView()

        self.__scene = QtGui.QGraphicsScene()

        self.__grview.setScene(self.__scene)
        widget.layout().addWidget(self.__grview, 0, 1, 2, 1)

        # details

        self.__detailsList = QtGui.QListWidget()

        widget.layout().addWidget(self.__detailsList, 1, 0, 1, 1)

        # toolbar

        self.__toolbar = self._create_toolbar()

    def _create_toolbar(self):

        # actions

        actions = list()

        exit_action = QtGui.QAction(QtGui.QIcon(''), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtGui.qApp.quit)
        actions.append(exit_action)
        

        new_servlet_action = QtGui.QAction(QtGui.QIcon(''), 'New Servlet', self)
        new_servlet_action.triggered.connect(self._new_servlet_callback)
        actions.append(new_servlet_action)


        update_action = QtGui.QAction(QtGui.QIcon(''), 'Update', self)
        update_action.triggered.connect(self._update_callback)
        actions.append(update_action)



        toolbar = self.addToolBar('Exit')

        for action in actions:
            toolbar.addAction(action)

        return toolbar
