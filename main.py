import os
import numpy
import pywt
from PIL import Image
from image import Noise, Filter, Mask
from skimage.metrics import peak_signal_noise_ratio


def noise():
    img = numpy.array(Image.open(image))
    Image.fromarray(Noise.random(img, 10000)).save(os.path.join(save_dir, '1.png'))
    Image.fromarray(Noise.salt_pepper(img, 0.05)).save(os.path.join(save_dir, '2.png'))
    Image.fromarray(Noise.gaussian(img)).save(os.path.join(save_dir, '3.png'))

    f = Filter()
    for i in range(1, 4):
        Image.fromarray(f.mean(numpy.array(Image.open(os.path.join(save_dir, f'{i}.png'))))).save(
            os.path.join(save_dir, f'{i}_1_1.png'))
        Image.fromarray(f.median(numpy.array(Image.open(os.path.join(save_dir, f'{i}.png'))))).save(
            os.path.join(save_dir, f'{i}_1_2.png'))
        Image.fromarray(f.gaussian(numpy.array(Image.open(os.path.join(save_dir, f'{i}.png'))))).save(
            os.path.join(save_dir, f'{i}_1_3.png'))

    for label in range(2):
        for n in range(1, 4):
            out = numpy.array(Image.open(os.path.join(save_dir, f'{n}.png')))
            img = numpy.copy(out)
            for i in range(img.shape[-1]):
                timg = img[:, :, i]
                ft = numpy.fft.fft2(timg)
                ft_shift = numpy.fft.fftshift(ft)
                mask = Mask.low_pass_filter(ft_shift, radius=200) if label == 0 else Mask.band_reject_filters(ft_shift,
                                                                                                              r_out=300,
                                                                                                              r_in=50)
                ft_shift = ft_shift * mask
                ft = numpy.fft.ifftshift(ft_shift)
                timg = numpy.abs(numpy.fft.ifft2(ft)).clip(0, 255)
                out[:, :, i] = numpy.uint8(timg)
            Image.fromarray(out).save(os.path.join(save_dir, f'{n}_2_{label + 1}.png'))

    threshold = 0.2
    modes = ['soft', 'hard', 'greater', 'less']
    for label in range(4):
        for n in range(1, 4):
            out = numpy.array(Image.open(os.path.join(save_dir, f'{n}.png')))
            img = numpy.copy(out)
            for i in range(img.shape[-1]):
                timg = img[:, :, i]
                dwt = pywt.wavedec2(timg, 'db8')
                for j in range(1, len(dwt)):
                    l = []
                    for k in range(len(dwt[j])):
                        l.append(pywt.threshold(dwt[j][k], threshold * numpy.max(dwt[j][k]), mode=modes[label]))
                    dwt[j] = tuple(l)
                timg = numpy.clip(pywt.waverec2(dwt, 'db8'), 0, 255)
                out[:, :, i] = numpy.uint8(timg)
            Image.fromarray(out).save(os.path.join(save_dir, f'{n}_3_{label + 1}.png'))


def psnr():
    img = numpy.array(Image.open(image))
    ans = {}
    for i in range(1, 4):
        name = os.path.join(save_dir, f'{i}.png')
        ans[name] = peak_signal_noise_ratio(img, numpy.array(Image.open(name)))
        for j in range(1, 4):
            for k in range(1, 5):
                name = os.path.join(save_dir, f'{i}_{j}_{k}.png')
                if os.path.exists(name):
                    ans[name] = peak_signal_noise_ratio(img, numpy.array(Image.open(name)))
    for k, v in ans.items():
        print(k.split('/')[-1], v)


if __name__ == '__main__':
    image = './images/1.jpg'
    save_dir = './images'
    noise()
    psnr()
