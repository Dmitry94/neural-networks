"""
    Script, which converts all cifar10 data to HDF5 format.
"""

import numpy as np
import h5py

import sys
sys.path.append('../..')
import ciraf as cr

from matplotlib import pyplot as plt

train_batches, test_batch = cr.read_ciraf_10(
    "../../content/ciraf/cifar-10-batches-py")

train_data = []
train_labels = []
for batch in train_batches:
    train_labels.append(batch['labels'])
    batch = batch['data'].reshape((batch['data'].shape[0], 3, 32, 32))
    batch = np.transpose(batch, axes=[0, 2, 3, 1])
    train_data.append(batch)

train_data = np.concatenate(train_data, axis=0)
train_labels = np.concatenate(train_labels, axis=0)
train_data = train_data.reshape((train_data.shape[0], 32, 32, 3))

test_data = test_batch['data'].reshape(
    (test_batch['data'].shape[0], 3, 32, 32))
test_data = np.transpose(test_data, axes=[0, 2, 3, 1])
test_labels = test_batch['labels']

train_hdf5 = h5py.File("../../content/ciraf/hdf5/train.hdf5", "w")
train_dset = train_hdf5.create_dataset("data", data=train_data)
train_lset = train_hdf5.create_dataset("labels", data=train_labels,
                                       dtype='uint8')
train_hdf5.close()

test_hdf5 = h5py.File("../../content/ciraf/hdf5/test.hdf5", "w")
test_dset = test_hdf5.create_dataset("data", data=test_data)
test_lset = test_hdf5.create_dataset("labels", data=test_labels,
                                     dtype='uint8')
test_hdf5.close()

train_hdf5 = h5py.File("../../content/ciraf/hdf5/train.hdf5", "r")
tt_d = train_hdf5["data"]
tt_l = train_hdf5["labels"]
print "Ok."
