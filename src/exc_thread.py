from threading import Thread

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

