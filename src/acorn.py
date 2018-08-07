def decrypt(key, iv, ad, p):
    adlen = len(ad)
    pclen = len(p)
    def acorn_state_update(a, b, c, d, e, f, g, m_bit, ca_bit, cb_bit, ctext=False):

        ks = (
            a[12] +  d[0] + c[4] + c[0] +
            f[5]*b[0] + f[5]*a[23] + f[5]*a[0] +
            b[0]*e[0] + b[0]*d[6] +  b[0]*d[0] +
            a[23]*e[0] + a[23]*d[6] + a[23]*d[0] +
            a[0]*e[0] + a[0]*d[6] + a[0]*d[0] +
            f[5]*e[0] + f[5]*d[6] + f[5]*d[0]
        )&1

        if ctext:
        	m_bit = (ks + m_bit)&1

        an = ( b[0] + a[23] + a[0] )&1
        bn = ( c[0] + b[5]  + b[0] )&1
        cn = ( d[0] + c[4]  + c[0] )&1
        dn = ( e[0] + d[6]  + d[0] )&1
        en = ( f[0] + e[3]  + e[0] )&1
        fn = ( g[0] + f[5]  + f[0] )&1
        gn = (
            (m_bit) + a[0] + c[0] +  b[0] + 1 +
            f[14]*a[23] +  a[23]*d[6]  +  d[6]*f[14] +
            f[0]*c[4] + e[3]*c[4] + e[0]*c[4] +
            f[0]*b[5] + e[3]*b[5] + e[0]*b[5] +
            ca_bit*e[3] + cb_bit*(ks)
            )&1

        a[:] = a[1:] + [an]
        b[:] = b[1:] + [bn]
        c[:] = c[1:] + [cn]
        d[:] = d[1:] + [dn]
        e[:] = e[1:] + [en]
        f[:] = f[1:] + [fn]
        g[:] = g[1:] + [gn]

        return ks
        #---------------------------------------------------------------------------
    a = [0]*61
    b = [0]*46
    c = [0]*47
    d = [0]*39
    e = [0]*37
    f = [0]*59
    g = [0]*4

    #---------------------------------------------------------------------------
    m = key + iv + [1] + [0]*1279
    ca = [1]*1536
    cb = [1]*1536

    for i in range(1536): acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])

    #---------------------------------------------------------------------------
    adlen = len(ad)
    m = ad + [1] + [0]*511
    ca = [1]*(adlen + 256) + [0]*256
    cb = [1]*(adlen + 512)

    for i in range(adlen + 512): acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])

    #---------------------------------------------------------------------------
    m  = p[:]
    ca = [1]*pclen
    cb = [0]*pclen

    ct = []
    z = []
    for i in range(pclen):
        ks = acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i], ctext=True)
        z.append(ks)
        ct.append((ks + m[i])&1)

    #---------------------------------------------------------------------------
    m  = [1] + [0]*511
    ca = [1]*256 + [0]*256
    cb = [0]*512

    for i in range(512): acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])

    #---------------------------------------------------------------------------
    m  = [0]*512
    ca = [1]*512
    cb = [1]*512

    taglen = 128
    tag = []
    for i in range(512):
        ks = acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])
        if i > 512 - taglen - 1 : tag.append(ks)

    return z, ct, tag
#===============================================================================
def encrypt(key, iv, ad, p):
    adlen = len(ad)
    pclen = len(p)
    #---------------------------------------------------------------------------
    def acorn_state_update(a, b, c, d, e, f, g, m_bit, ca_bit, cb_bit):
        ks = (
            a[12] +  d[0] + c[4] + c[0] +
            f[5]*b[0] + f[5]*a[23] + f[5]*a[0] +
            b[0]*e[0] + b[0]*d[6] +  b[0]*d[0] +
            a[23]*e[0] + a[23]*d[6] + a[23]*d[0] +
            a[0]*e[0] + a[0]*d[6] + a[0]*d[0] +
            f[5]*e[0] + f[5]*d[6] + f[5]*d[0]
        )&1

        an = ( b[0] + a[23] + a[0] )&1
        bn = ( c[0] + b[5]  + b[0] )&1
        cn = ( d[0] + c[4]  + c[0] )&1
        dn = ( e[0] + d[6]  + d[0] )&1
        en = ( f[0] + e[3]  + e[0] )&1
        fn = ( g[0] + f[5]  + f[0] )&1
        gn = (
            m_bit + a[0] + c[0] +  b[0] + 1 +
            f[14]*a[23] +  a[23]*d[6]  +  d[6]*f[14] +
            f[0]*c[4] + e[3]*c[4] + e[0]*c[4] +
            f[0]*b[5] + e[3]*b[5] + e[0]*b[5] +
            ca_bit*e[3] + cb_bit*ks
            )&1

        a[:] = a[1:] + [an]
        b[:] = b[1:] + [bn]
        c[:] = c[1:] + [cn]
        d[:] = d[1:] + [dn]
        e[:] = e[1:] + [en]
        f[:] = f[1:] + [fn]
        g[:] = g[1:] + [gn]

        return ks

    #---------------------------------------------------------------------------
    a = [0]*61
    b = [0]*46
    c = [0]*47
    d = [0]*39
    e = [0]*37
    f = [0]*59
    g = [0]*4

    #---------------------------------------------------------------------------
    m = key + iv + [1] + [0]*1279
    ca = [1]*1536
    cb = [1]*1536

    for i in range(1536): acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])

    #---------------------------------------------------------------------------
    adlen = len(ad)
    m = ad + [1] + [0]*511
    ca = [1]*(adlen + 256) + [0]*256
    cb = [1]*(adlen + 512)

    for i in range(adlen + 512): acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])

    #---------------------------------------------------------------------------
    m  = p[:]
    ca = [1]*pclen
    cb = [0]*pclen

    ct = []
    z = []
    for i in range(pclen):
        ks = acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])
        z.append(ks)
        ct.append((ks + m[i])&1)

    #---------------------------------------------------------------------------
    m  = [1] + [0]*511
    ca = [1]*256 + [0]*256
    cb = [0]*512

    for i in range(512): acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])

    #---------------------------------------------------------------------------
    m  = [0]*512
    ca = [1]*512
    cb = [1]*512

    taglen = 128
    tag = []
    for i in range(512):
        ks = acorn_state_update(a, b, c, d, e, f, g, m[i], ca[i], cb[i])
        if i > 512 - taglen - 1 : tag.append(ks)

    return z, ct, tag

#==========================================================
def pretty_print(s, l=32):
    return ('0'*(l-1)+(hex(int(''.join(map(str, s)), 2))[2:].replace('L','')))[-l:]
