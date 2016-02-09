import logging, socket
from PyQt4 import QtCore

import dispatcher, diagnosis_server, servlet



class DiagnosisService(QtCore.QThread):

    new_servlet = QtCore.pyqtSignal(object)
    disconnected_servlet = QtCore.pyqtSignal(object)

    def __init__(self, port=None):

        QtCore.QThread.__init__(self)

        self.__servlets = list()

        self.__dispatcher = dispatcher.EventDispatcher()

        self.__diagnosis_server = diagnosis_server.Server(port)
        
        self.__dispatcher.register(self.__diagnosis_server)

        diagnosis_server.new_servlet_signal.connect(
            self.new_servlet_callback)

        servlet.servlet_disconnected_signal.connect(
            self.servlet_disconnected_callback)
        

    def servlet_disconnected_callback(self, disconnected_servlet, **kwargs):
        self.__dispatcher.unregister(disconnected_servlet)
        self.__servlets.remove(disconnected_servlet)
        self.disconnected_servlet.emit(disconnected_servlet)

    @staticmethod
    def _get_servlet_style(servl):
        s = '{node [color="%0.4f %0.4f %0.4f" style=filled] %d}' \
            % (servl.color['h'],
               servl.color['s'],
               servl.color['v'],
               servl.get_dest_port())

        logging.debug('style: ' + s)

        return s

    def export_to_dot(self):

        associations = list()

        styles = map(self._get_servlet_style, self.__servlets)

        for crnt_servlet in self.__servlets:

            associations.extend(
                map(lambda s: '%d -- %d [len=2.0]' % (crnt_servlet.get_dest_port(),
                                            s['port']), crnt_servlet.get_peers()))

        dot = '''strict graph mygraph { 
        node [shape = circle];
        %s
        %s
        }''' \
            % (";\n".join(styles), ";\n".join(associations))

        return dot

    def update_all(self):

        for crnt_servlet in self.__servlets:
            crnt_servlet.request_status_update()

    def get_servlets(self):
        return self.__servlets


    def get_port(self):
        return self.__diagnosis_server.get_port()

    def new_servlet_callback(self, new_servlet, **kwargs):
        if type(new_servlet) is not servlet.Servlet:
            raise TypeError('expected a Servlet')
            
        self.__servlets.append(new_servlet)
        self.__dispatcher.register(new_servlet)
        self.new_servlet.emit(new_servlet)

    def run(self):

        while True:
            self.__dispatcher.handle_events()

    
