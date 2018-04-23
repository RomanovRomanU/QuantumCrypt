import random
from math import floor


# Hint functions sigma0, and sigma1
def sigma_0(x, q):
    return not(x >= -floor(q/4) and x <= floor(q/4))

def sigma_1(x, q):
    return not(x >= -floor(q/4) + 1 and x <= floor(q/4) + 1)

#Signal function
def sig(y, q):
    b = random.choice([0, 1])
    return sigma_1(y, q) if b == 1 else sigma_0(y, q)

# Reconciliation function
def mod2(x, q):
    w = sig(x, q)
    return ((x + w * (q-1) / 2) % q) % 2

# Round function
def round(x, p, q):
    x_1 = floor(p * x / q)
    if (x % 2 == 1) and (x_1 % 2 == 0):
        x_1 += 1
    if (x % 2 == 0) and (x_1 % 2 == 1):
        x_1 += 1
    return remove_bias(x_1, p, q)

def remove_bias(x_1, p, q):
    pass

def derive_a():
    pass

def sample():
    pass

def recover():
    pass

class PartyPerson:
    def __init__(self, n, sigma, q, p):
        self.n = n
        self.sigma = sigma
        self.q = q
        self.p = p


class Alice(PartyPerson):
    def request(self):
        # Party i
        # Generate 128-bit
        seed = random.randrange(1, 2**128)
        a = derive_a()
        self.s_i, self.e_i = sample(), sample()
        self.p_i = a * self.s_i + 2 * self.e_i
        # Send this (p`_i) to party j
        return round(self.p_i, self.p, self.q)

    def process_response(self, p_j, w_j):
        p_j_2 = recover(p_j, self.p, self.q)
        k_i = p_j_2 * self.s_i
        # Final shared key
        self.sk_i = mod2(k_i, w_j)

class Bob(PartyPerson):
    def response(self, p_i):
        a = derive_a()
        self.s_j, self.e_j = sample(), sample()
        self.p_j = a * self.s_j + 2 * self.e_j
        self.p_j_1 = round(self.p_j, self.p, self.q)
        self.p_i_2 = recover(self.p_i, self.p, self.q)
        self.k_j = self.p_i_2 * self.s_j
        self.w_j = sig(self.k_j)
        # Final shared key
        self.sk_j =  mod2(self.k_j, self.w_j)
        return self.p_j, self.w_j


class ProtocolController:
    def __init__(self, alice, bob):
        assert isinstance(alice, Alice)
        self.alice = alice
        assert isinstance(bob, Bob)
        self.bob = bob

    def __call__(self):
        alice = self.alice
        bob = self.bob
        p_i = alice.request()
        p_j, w_j = bob.response()

        alice.process_response(p_j, w_j)
        assert alice.sk_i == bob.sk_j
        print('Key exchange protocol succeed!!')
