import types
import logging


class Stop(Exception):
    pass

class Derail(Exception):
    pass

def run(chain, chain_name="main", **ctx):
    fchain = chain[:]

    f = fchain.pop(0)

    out = None

    while f:
        logging.debug('chain %s run %r from %r' % (chain_name, f, fchain))

        try:
            run = f
            f = None
            ret = run(upd_ctx=ctx, **ctx)

            if isinstance(ret, list):
                for add in ret:
                    fchain.insert(0, add)

            elif isinstance(ret, types.FunctionType):
                f = ret

            elif ret:
                ctx[run.__name__] = ret


        except Stop, e:
            break
        
        except Derail, e:
            logging.debug("derail to %r" % (e.args,))
            fchain = list(e.args)

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
