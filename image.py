import numpy
import random


class Noise:
    @staticmethod
    def random(img: numpy.array, number: int):
        img = numpy.copy(img)
        rows, cols, chn = img.shape
        for i in range(number):
            x = random.randint(0, rows - 1)
            y = random.randint(0, cols - 1)
            img[x, y, :] = 255
        return img

    @staticmethod
    def salt_pepper(img: numpy.array, prob: float):
        img = numpy.copy(img)
        assert 0 <= prob <= 1
        threshold = 1 - prob
        rows, cols, chn = img.shape
        for i in range(rows):
            for j in range(cols):
                rand = random.random()
                if rand < prob:
                    img[i, j, :] = 0
                elif rand > threshold:
                    img[i, j, :] = 255
        return img

    @staticmethod
    def gaussian(img: numpy.array, mean: float = 0, var: float = 0.001):
        img = numpy.copy(img)
        img = numpy.array(img, dtype=float) / 255
        noise = numpy.random.normal(mean, var ** 0.5, img.shape)
        img = img + noise
        img = numpy.clip(img, -1 if img.min() < 0 else 0, 1)
        img = numpy.uint8(img * 255)
        return img


class Filter:
    @staticmethod
    def pad(img: numpy.array, kernel_size: int = 3):
        assert kernel_size & 1
        padding = kernel_size // 2
        rows, cols, chn = img.shape
        padded = numpy.zeros((rows + padding * 2, cols + padding * 2, chn), dtype=float)
        padded[padding:padding + rows, padding:padding + cols, :] = numpy.copy(img)
        return rows, cols, chn, padding, padded

    def gaussian(self, img: numpy.array, kernel_size: int = 3, var: float = 1.3):
        rows, cols, chn, padding, padded = self.pad(img, kernel_size)

        kernel = numpy.zeros((kernel_size, kernel_size))
        for x in range(-padding, -padding + kernel_size):
            for y in range(-padding, -padding + kernel_size):
                kernel[x + padding, y + padding] = numpy.exp(-(x ** 2 + y ** 2) / (2 * (var ** 2)))
        kernel /= var * numpy.sqrt(2 * numpy.pi)
        kernel /= kernel.sum()

        out = numpy.copy(padded)

        for x in range(rows):
            for y in range(cols):
                for c in range(chn):
                    out[x + padding, y + padding, c] = numpy.sum(
                        kernel * padded[x:x + kernel_size, y:y + kernel_size, c])
        out = out.clip(0, 255)

        return numpy.uint8(out[padding:padding + rows, padding:padding + cols, :])

    def median(self, img: numpy.array, kernel_size: int = 3):
        rows, cols, chn, padding, padded = self.pad(img, kernel_size)

        out = numpy.copy(padded)

        for x in range(rows):
            for y in range(cols):
                for c in range(chn):
                    out[x + padding, y + padding, c] = numpy.median(padded[x:x + kernel_size, y:y + kernel_size, c])
        out = out.clip(0, 255)

        return numpy.uint8(out[padding:padding + rows, padding:padding + cols, :])

    def mean(self, img: numpy.array, kernel_size: int = 3):
        rows, cols, chn, padding, padded = self.pad(img, kernel_size)

        out = numpy.copy(padded)

        for x in range(rows):
            for y in range(cols):
                for c in range(chn):
                    out[x + padding, y + padding, c] = numpy.mean(padded[x:x + kernel_size, y:y + kernel_size, c])
        out = out.clip(0, 255)

        return numpy.uint8(out[padding:padding + rows, padding:padding + cols, :])


class Mask:
    @staticmethod
    def high_pass_filter(img: numpy.array, radius=80):
        r = radius

        rows, cols = img.shape
        center = int(rows / 2), int(cols / 2)

        mask = numpy.ones((rows, cols), numpy.uint8)
        x, y = numpy.ogrid[:rows, :cols]
        mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r * r
        mask[mask_area] = 0
        return mask

    @staticmethod
    def low_pass_filter(img: numpy.array, radius=100):
        r = radius

        rows, cols = img.shape
        center = int(rows / 2), int(cols / 2)

        mask = numpy.zeros((rows, cols), numpy.uint8)
        x, y = numpy.ogrid[:rows, :cols]
        mask_area = (x - center[0]) ** 2 + (y - center[1]) ** 2 <= r * r
        mask[mask_area] = 1
        return mask

    @staticmethod
    def band_reject_filters(img: numpy.array, r_out=300, r_in=35):
        rows, cols = img.shape
        crow, ccol = int(rows / 2), int(cols / 2)

        mask = numpy.zeros((rows, cols), numpy.uint8)
        center = [crow, ccol]
        x, y = numpy.ogrid[:rows, :cols]
        mask_area = numpy.logical_and(((x - center[0]) ** 2 + (y - center[1]) ** 2 >= r_in ** 2),
                                      ((x - center[0]) ** 2 + (y - center[1]) ** 2 <= r_out ** 2))
        mask[mask_area] = 1
        mask = 1 - mask
        return mask

    @staticmethod
    def band_pass_filters(img: numpy.array, r_out=300, r_in=35):
        rows, cols = img.shape
        crow, ccol = int(rows / 2), int(cols / 2)

        mask = numpy.zeros((rows, cols), numpy.uint8)
        center = [crow, ccol]
        x, y = numpy.ogrid[:rows, :cols]
        mask_area = numpy.logical_and(((x - center[0]) ** 2 + (y - center[1]) ** 2 >= r_in ** 2),
                                      ((x - center[0]) ** 2 + (y - center[1]) ** 2 <= r_out ** 2))
        mask[mask_area] = 1
        return mask
