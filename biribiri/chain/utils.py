
"""
View matcher shortcut
"""
def view(url, **kw):
    return match('view', url=url, found_view=None, **kw)

"""
Pattern-matching decorator

Runs decorated function only if chain context
matches provided pattern.

Example:

    @match(url='/')
    def index(**kw):
        ...


    biribiri.run([index], url='/')

If one nonkeyword argument passed, sets corresponding context key yo True.

Example:

    @match('view', url='/')
    def index(**kw):
        ...

    @match('view', found_view=None)
    def err404(**kw):
        ...


    biribiri.run([index, err404], url='/')

After first 'view' function matched, context variable 'view_found'
sets to True so err404 not matches

"""
def match(ftype='any', **pattern):
    def match_(f):
        def match__(**kw):

            for k,v in pattern.items():
                val = kw.get(k)
                if not (
                  val == v
                  or
                  (
                          isinstance(v, type)
                          and isinstance(val, v)
                  )
                  or
                  (
                      isinstance(v, type)
                      and isinstance(val, type)
                      and issubclass(val, v)
                  )):
                    return

            if 'upd_ctx' not in kw:
                return f(**kw)

            ctx = kw.get('upd_ctx') or {}
            ctx['found_%s' % ftype] = True

            return f


        if hasattr(f, "__name__"):
            match__.__name__ = '@match %s' % f.__name__
        return match__

    return match_

"""
Updates context with function return values
 if returned object is tuple with lenth greater
 or equal than decorator arguments list

Example:

    @upd_ctx('rendered')
    def render(obj=None, **kw):
        if not obj:
            return

        return (obj.__name__,)


Here if function render returns tuple of values
with lenth grater or equal to 1, context key 'rendered' 
sets to obj.__name__

Notice: last tuple argument returned to caller

Example:

    @upd_ctx('rendered')
    def render(obj=None, **kw):
        if not obj:
            return

        return (obj.__name__, [save_cache])


Here [save_cache] list would be returned to chain runner,
resulting add of function 'save_cache' to running schedule.

If function not returned tuple or tuple length is less
than args list, value is ignored

"""
def upd_ctx(*names):
    def upd_ctx_(f):
        def upd_ctx__(**kw):
            ret = f(**kw)
            if not ret:
                return

            ctx = kw.get('upd_ctx')
            if isinstance(ret, tuple) and len(ret) >= len(names):
                ctx.update(zip(names, ret))

                return ret[-1]

            elif len(names) == 1:
                ctx[names[0]] = ret


        upd_ctx__.__name__ = '@upd_ctx %s' % f.__name__
        return upd_ctx__

    return upd_ctx_
