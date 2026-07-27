import sys

# ============ BigInt 底层大数运算 (Python 版) ============
biRadixBits = 16
bitsPerDigit = 16
biRadix = 65536
biHalfRadix = 32768
biRadixSquared = 4294967296
maxDigitVal = 65535
hexToChar = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]

max_digits = 0

class BigInt:
    def __init__(self, flag=False):
        if flag:
            self.digits = None
        else:
            self.digits = [0] * max_digits
        self.isNeg = False

def set_max_digits(value):
    global max_digits, ZERO_ARRAY, big_zero, big_one
    max_digits = value
    ZERO_ARRAY = [0] * max_digits
    big_zero = BigInt()
    big_one = BigInt()
    big_one.digits[0] = 1

def bi_from_hex(s):
    result = BigInt()
    k = len(s)
    j = 0
    for i in range(k, 0, -4):
        start = max(i - 4, 0)
        result.digits[j] = int(s[start:i], 16)
        j += 1
    return result

def bi_high_index(x):
    i = len(x.digits) - 1
    while i > 0 and x.digits[i] == 0:
        i -= 1
    return i

def bi_copy(bi):
    result = BigInt(True)
    result.digits = bi.digits.copy()
    result.isNeg = bi.isNeg
    return result

def bi_add(x, y):
    ml = max(len(x.digits), len(y.digits)) + 1
    result = BigInt()
    result.digits = [0] * ml
    carry = 0
    for i in range(ml):
        xd = x.digits[i] if i < len(x.digits) else 0
        yd = y.digits[i] if i < len(y.digits) else 0
        s = xd + yd + carry
        result.digits[i] = s & 0xffff
        carry = 1 if s >= biRadix else 0
    return result

def bi_subtract(x, y):
    result = BigInt()
    result.digits = [0] * len(x.digits)
    borrow = 0
    for i in range(len(x.digits)):
        yd = y.digits[i] if i < len(y.digits) else 0
        diff = x.digits[i] - yd - borrow
        result.digits[i] = diff & 0xffff
        borrow = 1 if diff < 0 else 0
    return result

def bi_multiply(x, y):
    xl = len(x.digits); yl = len(y.digits)
    result = BigInt()
    result.digits = [0] * (xl + yl + 1)
    for i in range(xl):
        if x.digits[i] == 0: continue
        carry = 0
        for j in range(yl):
            v = result.digits[i+j] + x.digits[i] * y.digits[j] + carry
            result.digits[i+j] = v & 0xffff
            carry = v >> 16
        result.digits[i+yl] = carry
    return result

def bi_shift_right(x, n):
    result = BigInt()
    result.digits = [0] * len(x.digits)
    shift = n // 16
    for i in range(len(x.digits)-shift):
        if i+shift < len(x.digits):
            val = x.digits[i+shift] >> (n%16)
            if i+shift+1 < len(x.digits):
                val |= (x.digits[i+shift+1] & 0xffff) << (16 - n%16)
            result.digits[i] = val
    return result

def bi_shift_left(x, n):
    result = BigInt()
    result.digits = [0]*(len(x.digits)+n//16+1)
    shift = n//16
    for i in range(len(x.digits)):
        result.digits[i+shift] = x.digits[i]
    if n%16:
        for i in range(len(result.digits)):
            result.digits[i] <<= (n%16)
    return result

def bi_num_bits(x):
    n = bi_high_index(x)
    if n < 0: return 0
    d = x.digits[n]; bits = (n+1)*16
    while d: d >>= 1; bits -= 1
    return bits

def bi_compare(x, y):
    xl = len(x.digits); yl = len(y.digits)
    if x.isNeg != y.isNeg: return -1 if x.isNeg else 1
    for i in range(max(xl,yl)-1,-1,-1):
        xd = x.digits[i] if i<xl else 0
        yd = y.digits[i] if i<yl else 0
        if xd != yd: return 1 if xd>yd else -1
    return 0

def bi_divide_by_radix_power(x, n):
    result = BigInt()
    shift = n//16
    if len(x.digits) <= shift:
        result.digits = [0]; return result
    result.digits = [0]*(len(x.digits)-shift)
    for i in range(len(result.digits)):
        result.digits[i] = x.digits[i+shift]
    return result

def bi_modulo_by_radix_power(x, n):
    result = BigInt()
    shift = n//16
    result.digits = [0]*min(shift, len(x.digits))
    for i in range(len(result.digits)):
        result.digits[i] = x.digits[i]
    return result

def bi_multiply_by_radix_power(x, n):
    result = BigInt()
    result.digits = [0]*(len(x.digits)+n)
    for i in range(len(x.digits)):
        result.digits[i+n] = x.digits[i]
    return result

def bi_multiply_digit(x, y):
    result = BigInt()
    result.digits = [0]*(len(x.digits)+1)
    carry = 0
    for i in range(len(x.digits)):
        v = x.digits[i]*y + carry
        result.digits[i] = v & 0xffff
        carry = v >> 16
    result.digits[len(x.digits)] = carry
    return result

def bi_divide_modulo(a, b):
    c = bi_num_bits(a); d = bi_num_bits(b); e = b.isNeg
    if d == 0: return [BigInt(), BigInt()]
    if d > c:
        if a.isNeg:
            f = bi_copy(big_one); f.isNeg = not b.isNeg
            a.isNeg=False; b.isNeg=False
            g = bi_subtract(b,a)
            a.isNeg=True; b.isNeg=e
        else:
            f = BigInt(); g = bi_copy(a)
        return [f,g]
    f = BigInt(); f.digits = [0]*max_digits; g = bi_copy(a)
    if len(b.digits)<=0: return [BigInt(), BigInt()]
    h = (d+15)//16-1
    if h<0: h=0
    i = 0
    while h<len(b.digits) and b.digits[h] < biHalfRadix:
        b = bi_shift_left(b,1); i+=1; d+=1
        h = (d+15)//16-1
        if h>=len(b.digits): h=len(b.digits)-1
    g = bi_shift_left(g,i); c+=i
    j = (c+15)//16-1
    if j-h>=0:
        k = bi_multiply_by_radix_power(b, j-h)
        while bi_compare(g,k) != -1:
            if j-h < len(f.digits): f.digits[j-h] += 1
            g = bi_subtract(g,k)
    l = j
    while l>h and l>=0:
        m = g.digits[l] if l<len(g.digits) else 0
        n_ = g.digits[l-1] if l-1<len(g.digits) and l-1>=0 else 0
        o = g.digits[l-2] if l-2<len(g.digits) and l-2>=0 else 0
        p = b.digits[h] if h<len(b.digits) else 0
        q = b.digits[h-1] if h-1<len(b.digits) and h-1>=0 else 0
        if p==0: p=1
        idx = l-h-1
        if idx>=0 and idx<len(f.digits):
            if m==p: f.digits[idx] = maxDigitVal
            else: f.digits[idx] = (m*biRadix + n_)//p
        else: break
        r = f.digits[idx]*(p*biRadix+q)
        s = m*biRadixSquared + n_*biRadix + o
        while r>s and f.digits[idx]>0:
            f.digits[idx]-=1
            r = f.digits[idx]*(p*biRadix|q)
            s = m*biRadix*biRadix + n_*biRadix + o
        k = bi_multiply_by_radix_power(b, l-h-1)
        g = bi_subtract(g, bi_multiply_digit(k, f.digits[idx]))
        if g.isNeg: g = bi_add(g,k); f.digits[idx]-=1
        l -= 1
    g = bi_shift_right(g,i)
    f.isNeg = (a.isNeg != e)
    if a.isNeg:
        f = bi_add(f,big_one) if e else bi_subtract(f,big_one)
        b = bi_shift_right(b,i); g = bi_subtract(b,g)
    if g.digits[0]==0 and bi_high_index(g)==0: g.isNeg=False
    return [f,g]

def bi_divide(x,y): return bi_divide_modulo(x,y)[0]

# ============ Barrett 模约减 ============
class BarrettMu:
    def __init__(self, m):
        self.modulus = bi_copy(m)
        self.k = bi_high_index(self.modulus)+1
        b = BigInt(); b.digits = [0]*(2*self.k+1); b.digits[2*self.k]=1
        self.mu = bi_divide(b, self.modulus)
        self.bkplus1 = BigInt()
        self.bkplus1.digits = [0]*(self.k+2); self.bkplus1.digits[self.k+1]=1
    def modulo(self, x):
        q1 = bi_divide_by_radix_power(x, self.k-1)
        q2 = bi_multiply(q1, self.mu)
        q3 = bi_divide_by_radix_power(q2, self.k+1)
        r1 = bi_modulo_by_radix_power(x, self.k+1)
        r2 = bi_multiply(q3, self.modulus)
        r3 = bi_modulo_by_radix_power(r2, self.k+1)
        r = bi_subtract(r1, r3)
        if r.isNeg: r = bi_add(r, self.bkplus1)
        while bi_compare(r, self.modulus) >= 0:
            r = bi_subtract(r, self.modulus)
        return r
    def multiply_mod(self, x, y):
        return self.modulo(bi_multiply(x,y))
    def pow_mod(self, x, y):
        result = BigInt(); result.digits = [0]*max_digits; result.digits[0]=1
        a = x; e = y
        while True:
            if (e.digits[0]&1)!=0: result = self.multiply_mod(result,a)
            e = bi_shift_right(e,1)
            if e.digits[0]==0 and bi_high_index(e)==0: break
            a = self.multiply_mod(a,a)
        return result

# ============ RSA 密钥 ============
class RSAKeyPair:
    def __init__(self, e, d, m):
        self.e = bi_from_hex(e)
        self.d = bi_from_hex(d)
        self.m = bi_from_hex(m)
        self.chunk_size = 2*bi_high_index(self.m)
        self.barrett = BarrettMu(self.m)

def digit_to_hex(a):
    c = ""
    for _ in range(4):
        c = hexToChar[a&15] + c; a >>= 4
    return c

def bi_to_hex(x):
    bi_high_index(x)
    r = ""
    for i in range(bi_high_index(x), -1, -1):
        r += digit_to_hex(x.digits[i])
    return r

def encrypted_string(key, s):
    arr = [ord(c) for c in s]
    chunk = key.chunk_size
    while len(arr)%chunk != 0: arr.append(0)
    result = ""
    for i in range(0, len(arr), chunk):
        f = BigInt()
        for j in range(chunk):
            if i+j < len(arr):
                f.digits[j] = arr[i+j]
                if i+j+1 < len(arr): f.digits[j] += arr[i+j+1] << 8
        g = key.barrett.pow_mod(f, key.e)
        h = bi_to_hex(g)
        while len(h) < 2*key.chunk_size: h = "0"+h
        result += h
    return result

# 测试
if __name__ == "__main__":
    set_max_digits(131)
    rsa_key = RSAKeyPair(
        "010001", "",
        "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    )
    result = encrypted_string(rsa_key, "GuGTIppgmQ4aoY3I")
    print(f"result: {result}")
    print(f"length: {len(result)}")
    # 检查是否全部是 0
    non_zero = sum(1 for c in result if c != '0')
    print(f"non-zero chars: {non_zero}")
