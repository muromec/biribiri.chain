import types
import logging
from time import time
import sys
import traceback


class Stop(Exception):
    pass

class Derail(Exception):
    pass

def exc_raise(exc, **kw):
    logging.error("chain failed %s" %
            str.join("",traceback.format_exception(*exc))
    )
    raise Stop()


def run(chain, chain_name="main", exception_handler=exc_raise, **ctx):
    fchain = chain[:]

    f = fchain.pop(0)
    time_start = time()


    while f:
        time_pre = time()

        try:
            run = f
            f = None
            ret = run(upd_ctx=ctx, **ctx)

            if isinstance(ret, list):
                for add in ret:
                    fchain.insert(0, add)

            elif isinstance(ret, types.FunctionType):
                f = ret

        except Stop, e:
            break
        
        except Derail, e:
            logging.debug("derail to %r" % (e.args,))
            fchain = list(e.args)
        except Exception, e:
            # if failed at failing, just die
            if run == exception_handler:
                raise

            f = exception_handler
            ctx['exc'] = sys.exc_info()
            continue
        finally:
            delta = time() - time_pre
            if delta > 1:
                log_f = logging.warning
            else:
                log_f = logging.debug

            all_delta = time() - time_start
            if all_delta > 0.5:
                break

            log_f('run %r in %f from %r' % (run, delta, fchain))

        if not f and fchain:
            f = fchain.pop(0)

    return ctx


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    def x(**ctx):
        print 'x', ctx

    def y(**ctx):
        print 'y', ctx

    def move(point, **ctx):
        print 'move to', point
        px,py = point

        if not (px or py):
            raise Derail(x,y)

    def zog(upd_ctx, **ctx):
        if 'point' in ctx:
            return

        upd_ctx.update({
                "point": (0,0),
        })

        return [move]

    print run([x, y, zog])
