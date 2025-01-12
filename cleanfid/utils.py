import numpy as np
import torch
import torchvision
from PIL import Image
from cleanfid.resize import build_resizer
import zipfile


class ResizeDataset(torch.utils.data.Dataset):
    """
    A placeholder Dataset that enables parallelizing the resize operation
    using multiple CPU cores

    files: list of all files in the folder
    np_images: list of numpy images
    fn_resize: function that takes an np_array as input [0,255]
    """

    def __init__(self, files, mode, size=(299, 299), np_images: list = None, fdir=None):
        self.files = files
        self.np_images = np_images
        self.fdir = fdir
        self.transforms = torchvision.transforms.ToTensor()
        self.size = size
        self.fn_resize = build_resizer(mode)

    def __len__(self):
        if self.files is not None:
            return len(self.files)
        else:
            assert self.np_images is not None
            return len(self.np_images)

    def __getitem__(self, i):
        if self.files is not None:
            path = str(self.files[i])
            if self.fdir is not None and ".zip" in self.fdir:
                with zipfile.ZipFile(self.fdir).open(path, "r") as f:
                    img_np = np.array(Image.open(f).convert("RGB"))
            if ".npy" in path:
                img_np = np.load(path)
            else:
                img_pil = Image.open(path).convert("RGB")
                img_np = np.array(img_pil)
        else:
            img_np = self.np_images[i]

        # fn_resize expects a np array and returns a np array
        img_resized = self.fn_resize(img_np)

        # ToTensor() converts to [0,1] only if input in uint8
        if img_resized.dtype == "uint8":
            img_t = self.transforms(np.array(img_resized)) * 255
        elif img_resized.dtype == "float32":
            img_t = self.transforms(img_resized)
        else:
            raise NotImplementedError

        return img_t


EXTENSIONS = {"bmp", "jpg", "jpeg", "pgm", "png", "ppm", "tif", "tiff", "webp", "npy"}
