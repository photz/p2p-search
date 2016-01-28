import logging, select

# why has this not been defined in the module?
if not "EPOLLRDHUP" in dir(select):
    select.EPOLLRDHUP = 0x2000

class EventDispatcher(object):

    CALLBACK_NAMES = {
        'readable_callback' : select.EPOLLIN,
        'writeable_callback' : select.EPOLLOUT,
        'hangup_callback' : select.EPOLLRDHUP,
        'error_callback' : select.EPOLLERR
    }

    HANDLE_ATTR_NAME = 'handle'

    def __init__(self):
        self.__epoll = select.epoll()
        self.__fds = {}

    def handle_events(self, timeout=-1):
        for fd, events in self.__epoll.poll(timeout):

                assert fd in self.__fds

                obj = self.__fds[fd]

                for callback_name, eventmask \
                    in EventDispatcher.CALLBACK_NAMES.items():

                    if events & eventmask:

                        assert hasattr(obj, callback_name)
                        assert callable(getattr(obj, callback_name))

                        getattr(obj, callback_name)()

                
    def register(self, obj):
        if not self.__has_handle(obj):
            raise TypeError('only objects that expose a handle attr ' +
                            'can be registered')

        handle = self.__get_handle(obj)

        if handle in self.__fds:
            raise ValueError('it seems that this object has already ' +
                             'been registered')
        
        self.__fds[handle] = obj

        self.__epoll.register(handle, self.__get_eventmask(obj))

        logging.debug('%s has been registered' % type(obj))

    def unregister(self, obj):
        if not self.__has_handle(obj):
            raise TypeError('the object given has no handle attribute')

        handle = self.__get_handle(obj)

        if handle not in self.__fds:
            raise ValueError('cannot be unregistered because unknown')

        del self.__fds[handle]

        self.__epoll.unregister(handle)

    def is_registered(self, obj):
        if not self.__has_handle(obj):
            raise TypeError('the object given has no handle attribute')

        handle = self.__get_handle(obj)

        return self.__fds.get(handle) is obj

    @staticmethod
    def __get_handle(obj):
        return getattr(obj, EventDispatcher.HANDLE_ATTR_NAME)

    @staticmethod
    def __has_handle(obj):
        return hasattr(obj, EventDispatcher.HANDLE_ATTR_NAME)        
            

    @staticmethod
    def __get_eventmask(obj):

        eventmask = 0

        for callback_name, event in EventDispatcher.CALLBACK_NAMES.items():
            if hasattr(obj, callback_name) \
               and callable(getattr(obj, callback_name)):

                eventmask |= event

        return eventmask
