from threading import Thread, Event

class ExcThread(Thread):

    def run(self):
        self.exc = None
        try:
            # Possibly throws an exception
            #threading.Thread.start(self)
            super().run()

        except:
            print('made it to exc thread exception block')
            import sys
            self.exc = sys.exc_info()
            # Save details of the exception thrown but don't rethrow,
            # just complete the function

    def join(self):
        super().join()
        if self.exc:
            msg = "Thread '%s' threw an exception: %s" % (self.getName(), self.exc[1])
            new_exc = Exception(msg)
            raise new_exc.with_traceback(self.exc[2])

    """
    def is_started(self):
        '''
        A thread is started if the thread has called start() already.
        This matters because once start() is called a thread can't call it
        again.
        Furthermore, join() can only be called once it has been started
        '''
        return self._started.is_set()
    """
