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
    # FIXME: вот здесь ну никак не получаеться x_1 < p (я пока добавил % p)
    x_1 = floor(p * x / q) % p

    if (x % 2 == 1) and (x_1 % 2 == 0):
        x_1 += 1
    if (x % 2 == 0) and (x_1 % 2 == 1):
        x_1 += 1
    return remove_bias(x_1, p, q)

# TODO: реально считать bias
def get_bias_positions(p, q):
    return (
        0,455,888,1333,1776,2221,2666,3109,354,3997,4442,4885,5339,
        5775,6218,6663,7106
        )

def remove_bias(x_1, p, q):
    if not(x_1 >= 0 and x_1 <= p):
        raise ValueError('x_1 is incorrect!')
    pos = get_bias_positions(p, q)
    if x_1 in pos:
        rnd = random.choice([0,1])
        if rnd == 1:
            x_1 += 2
    return x_1


# Coeficient a_i of polynomial a in Rq
def derive_a(q):
    return random.randrange(0, q)

# TODO: вместо обычного распределния, сделать то, что в лабе
def sample(q):
    return random.randrange(0, q)


def recover(x_1, p, q):
    if not (x_1 >= 0) and (x_1 <= p):
        raise ValueError('x_1 is incorrect')
    x_2 = floor(x_1 * q / p)
    if (x_1 % 2 == 1) and (x_2 % 2 == 0):
        x_2 += 1
    elif (x_1 % 2 == 0) and (x_2 % 2 == 1):
        x_2 += 1
    return x_2


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
        a = derive_a(seed)
        # TODO: использовать тут распределение по сигма
        self.s_i, self.e_i = sample(self.q), sample(self.q)
        self.p_i = a * self.s_i + 2 * self.e_i
        # Send this (p`_i_1) to party j
        p_i_1 = round(self.p_i, self.p, self.q)

        return p_i_1, seed

    def process_response(self, p_j_1, w_j):
        p_j_2 = recover(p_j_1, self.p, self.q)
        k_i = p_j_2 * self.s_i
        # Final shared key
        self.sk_i = mod2(k_i, w_j)


class Bob(PartyPerson):
    def response(self, p_i_1, seed):
        # TODO: тут как-то должне использоваться seed
        a = derive_a(self.q)
        # TODO: использовать тут распределение по сигма
        self.s_j, self.e_j = sample(self.q), sample(self.q)
        self.p_j = a * self.s_j + 2 * self.e_j

        self.p_j_1 = round(self.p_j, self.p, self.q)

        self.p_i_2 = recover(p_i_1, self.p, self.q)

        self.k_j = self.p_i_2 * self.s_j
        self.w_j = sig(self.k_j, self.q)
        # Final shared key
        self.sk_j =  mod2(self.k_j, self.w_j)
        print('p_j_1: {}; p_i_2:{}; k_j: {}, w_j:{}; sk_j:{}'
              .format(p_i_1, self.p_i_2, self.k_j, self.w_j, self.sk_j))
        return self.p_j_1, self.w_j


class ProtocolController:

    def __call__(self, n, sigma, q, p):
        alice = Alice(n, sigma, q, p)
        bob = Bob(n, sigma, q, p)

        p_i, seed = alice.request()
        # TODO: тут передавать seed вторым аргументом
        p_j, w_j = bob.response(p_i, None)
        print('P_j :{} \n w_j: {}\nsk_j: {}'.format(p_j, w_j, bob.sk_j))
        alice.process_response(p_j, w_j)
        assert alice.sk_i == bob.sk_j
        print(alice.sk_i, bob.sk_j)
        print('Key exchange protocol succeed!!')


if __name__ == '__main__':
    n = 512
    sigma = 4.19
    q = 120833
    p = 7551

    ProtocolController()(n, sigma, q, p)
