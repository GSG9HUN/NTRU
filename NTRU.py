from math import trunc
from sympy import symbols, Poly, GF
import random

# Paraméterek
N = 41
p = 3
q = 97

# Polinom változó
x = symbols('x')

# Random polinom generálása
def generate_random_polynomial(N, domain, density=0.3):
    coeffs = [random.choice([-1, 0, 1]) if random.random() < density else 0 for _ in range(N)]
    return Poly(coeffs, x, domain=domain)

# Szöveg konvertálása polinom blokkokra
def text_to_poly_blocks(text, domain, block_size):
    binary_string = ''.join(f'{len(text):016b}')
    binary_string += ''.join(f'{ord(char):016b}' for char in text)
    binary_coeffs = [int(bit) for bit in binary_string]

    blocks = [
        Poly(binary_coeffs[i:i + block_size] + [0] * (block_size - len(binary_coeffs[i:i + block_size])),
             x, domain=domain)
        for i in range(0, len(binary_coeffs), block_size)
    ]

    return blocks

#Titkosítási függvény
def encrypt(message_poly, h):
    r = generate_random_polynomial(N, GF(q), density=0.3)
    e = (r * h + message_poly) % Poly(x ** N - 1, x, domain=GF(q))
    return e


# Visszafejtési függvény
def decrypt(e, f):
    a = (f * e) % Poly(x ** N - 1, x, domain=GF(q))

    a_coeffs = [((coeff + q // 2) % q) - q // 2 for coeff in a.all_coeffs()]
    a = Poly(a_coeffs, x, domain=GF(q))

    m_coeffs = [coeff % p for coeff in a.all_coeffs()]
    m = Poly(m_coeffs, x, domain=GF(p))
    return m


# Kulcsgenerálás mod q mezőben invertálhatóság ellenőrzéssel
def generate_keys():
    while True:
        F_x = generate_random_polynomial(N, GF(q))
        f_q = Poly(1 + p * F_x, x, domain=GF(q))  # f(x) mod q mezőben
        g_q = generate_random_polynomial(N, GF(q))

        try:
            # Invertálhatóság ellenőrzése
            f_inv_q = f_q.invert(Poly(x ** N - 1, x, domain=GF(q)))
            h = (p * g_q * f_inv_q) % Poly(x ** N - 1, x, domain=GF(q))
            return (f_q, h), (f_q, f_inv_q)
        except Exception as e:
            # Ha nem invertálható, újra generálunk egy polinomot
            continue

# Polinom együtthatóinak visszaszerzése vezető nullákkal
def get_all_coeffs_with_leading_zeros(poly, degree):
    coeffs = [poly.coeff_monomial(x ** i) for i in range(degree, -1, -1)]
    return coeffs


# Fő függvény
if __name__ == "__main__":
    (private_key, public_key), (f, f_inv_p) = generate_keys()
    print(f"Privát kulcs: {private_key}")
    print(f"Publikus kulcs: {public_key}")

    message_text = "A posztkvantum algoritmusok olyan kriptográfiai módszerek, amelyeket a kvantumszámítógépek által jelentett fenyegetések ellen fejlesztettek ki. Míg a klasszikus algoritmusok, mint az RSA vagy az elliptikus görbe kriptográfia, sebezhetővé válhatnak a kvantumalgoritmusok, például Shor algoritmusa miatt, a posztkvantum algoritmusok olyan matematikai problémákon alapulnak, amelyeket a kvantumszámítógépek sem tudnak hatékonyan megoldani. Ilyen problémák például a rácsalapú, a kódoláson alapuló, a többváltozós polinomiális, valamint a hashelési problémák. Az ilyen algoritmusok kulcsfontosságúak a jövőben, hogy biztosítsák az adatok védelmét a kvantuminformatikai korszakban."
    binary_message = text_to_poly_blocks(message_text, GF(q), N)

    encrypted_blocks = [encrypt(block, public_key) for block in binary_message]

    decrypted_block = []
    for i in encrypted_blocks:
        decrypted_block.append(decrypt(i, f))

    all_coeffs = []
    for i in decrypted_block:
        all_coeffs.append(get_all_coeffs_with_leading_zeros(i, N - 1))

    first_16 = all_coeffs[0][:16]
    binary_string = ''.join(str(bit) for bit in first_16)

    # Binárisból decimális számmá alakítás
    decimal_value = int(binary_string, 2)
    print("Decimális érték:", decimal_value)

    all_bits = len(decrypted_block) * N
    txt_lengt = decimal_value

    bits = []
    k = 0
    skip_first_16 = True  # Flag, hogy átugorjuk-e az első 16 bitet

    for i in all_coeffs:
        if skip_first_16:
            i = i[16:]  # Csak a 17. bittől kezdve használjuk az elemeket
            skip_first_16 = False

        for j in i:
            if k == txt_lengt * 16:
                break
            bits.append(j)
            k += 1

    binary_string = ''.join(str(bit) for bit in bits)
    text = ''.join(chr(int(binary_string[i:i + 16], 2)) for i in range(0, len(binary_string), 16))
    print("Szöveg:", text)
