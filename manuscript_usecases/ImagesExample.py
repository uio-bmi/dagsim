import numpy as np
from PIL import Image as PILImage


def uniform(*args, **kwargs):
    return np.random.uniform(*args, **kwargs)


def binomial(*args, **kwargs):
    return np.random.binomial(*args, **kwargs)


def create_circular_mask():
    randC1 = np.random.randint(low=10, high=246)
    randC2 = np.random.randint(low=10, high=246)

    Y, X = np.ogrid[:256, :256]
    dist_from_center = np.sqrt((X - randC1) ** 2 + (Y - randC2) ** 2)

    mask = (dist_from_center <= 10) * 256
    return mask


def complement_binomial(U1):
    return np.random.binomial(1, 1 - U1)


def sigmoid_binomial(C, Dnum, Dstr):
    if Dstr == "H":
        out = 0.75 * Dnum + 0.5 * C + 0.25
    else:
        out = 2.5 * Dnum + 1.75 * C - 0.25
    out = 1 / (1 + np.exp(-out))
    out = np.random.binomial(1, out)
    return out


def drawImage(H, V, R, C, output_path):
    image = np.zeros(shape=(256, 256))
    randInd = np.random.randint(low=1, high=10000)
    if H == 1:
        randPosH = np.random.randint(low=10, high=246)
        image[randPosH - 5:randPosH + 5, :] = 256

    if V == 1:
        randPosV = np.random.randint(low=10, high=246)
        image[:, randPosV - 5:randPosV + 5] = 256

    if C == 1:
        mask = create_circular_mask()
        image = image + mask

    if R == 1:
        TLy = np.random.randint(low=0, high=226)  # y-coordinate of the top-left corner
        TLx = np.random.randint(low=0, high=206)  # x-coordinate of the top-left corner

        image[TLy: TLy+30, TLx: TLx+50] = 256

    image = image + np.random.binomial(1, 0.005, size=(256, 256)) * 256
    image = PILImage.fromarray(image)
    image = image.convert("L")
    image.save(output_path + "/" + str(randInd) + ".png")


if __name__ == "__main__":
    drawImage(0, 0, 1, 0, ".")
