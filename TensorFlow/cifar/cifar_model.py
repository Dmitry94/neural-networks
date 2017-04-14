"""
    Cifar10 Network model.
"""

# pylint: disable=C0103
# pylint: disable=C0330

from collections import namedtuple

import tensorflow as tf
slim = tf.contrib.slim

ModelParams = namedtuple('ModelParams', ['filters_counts',
                                         'conv_ksizes', 'conv_strides',
                                         'pool_ksizes', 'pool_strides',
                                         'fc_sizes', 'dropouts'],
                         verbose=True)


def _tensor_summary(tensor):
    """
        Generates summury for some tensor.
        Summary it's histogram and sparsity.
    """
    tensor_name = tensor.op.name
    tf.summary.histogram(tensor_name, tensor)

    # Tensor sparsiry, i.e. zeros_count / all
    tf.summary.scalar(tensor_name + '/sparsity',
                      tf.nn.zero_fraction(tensor))

def conv_pool_drop_2d(in_data, filters_count, conv_ksize, conv_stride,
                      pool_ksize, pool_stride, keep_prob, scope):
    """
        Creating three layers: conv, max_pool, dropout.

        Parameters:
        -------
            in_data: input tensor of data
            conv_ksize: conv kernel size
            conv_stride: conv stride
            pool_ksize: pool kernel size
            pool_stride: pool stride
            keep_prob: probability of that neuron is active
            scope: scope name

        Returns:
        -------
            Out after conv, max pool and drop.
    """
    out = slim.conv2d(in_data, filters_count, kernel_size=conv_ksize,
                      stride=conv_stride, scope=scope + '/conv')
    out = slim.max_pool2d(out, kernel_size=pool_ksize, stride=pool_stride,
                          scope=scope + '/pool')
    out = slim.dropout(out, keep_prob, scope=scope + '/dropout')

    return out

def fc_drop(in_data, fc_size, keep_prob, scope):
    """
        Creates two layers: full connected and dropout.

        Parameters:
        -------
            in_data: input tensor of data
            fc_size: size of full connected layer
            keep_prob: probability of that neuron is active
            scope: scope name

        Returns:
        -------
            Out after fc and dropout.
    """
    out = slim.fully_connected(in_data, fc_size, scope=scope + 'fc')
    out = slim.dropout(out, keep_prob, scope=scope + '/dropout')

    return out


def inference(images, model_params):
    """
        Builds cifar10 model.

        Parameters:
        -------
            images: input data
            model_params: ModelParams objects, describes all layers

        Returns:
        -------
            Logits for each label
    """
    filters_counts = model_params.filters_counts
    conv_ksizes = model_params.conv_ksizes
    conv_strides = model_params.conv_strides
    pool_ksizes = model_params.pool_ksizes
    pool_strides = model_params.pool_strides
    fc_sizes = model_params.fc_sizes
    dropouts = model_params.dropouts

    if not filters_counts:
        raise ValueError("List of convolutional layers filters is empty!")
    if not conv_ksizes:
        raise ValueError("List of convolutional layers kernel sizes is empty!")
    if not pool_ksizes:
        raise ValueError("List of pool layers kernel sizes is empty!")
    if not fc_sizes:
        raise ValueError("List of full connected layers sizes is empty!")

    conv_layers_count = len(filters_counts)
    if len(conv_ksizes) < conv_layers_count:
        conv_ksizes.extend([conv_ksizes[-1]] * (conv_layers_count - len(conv_ksizes)))

    if not conv_strides:
        conv_strides = [1] * conv_layers_count
    elif len(conv_strides) < conv_layers_count:
        conv_strides.extend([conv_strides[-1]] * (conv_layers_count - len(conv_strides)))

    if len(pool_ksizes) < conv_layers_count:
        pool_ksizes.extend([pool_ksizes[-1]] * (conv_layers_count - len(pool_ksizes)))

    if not pool_strides:
        pool_strides = pool_ksizes
    elif len(pool_strides) < conv_layers_count:
        pool_strides.extend([pool_strides[-1]] * (conv_layers_count - len(pool_strides)))

    dropouts_count = conv_layers_count + len(fc_sizes) - 1
    if len(dropouts) < dropouts_count:
        dropouts.extend([1] * (dropouts_count - len(dropouts)))

    with tf.device('/CPU:0'):
        with slim.arg_scope([slim.conv2d, slim.fully_connected],
                            activation_fn=tf.nn.relu,
                            weights_initializer=slim.xavier_initializer()):
            net = slim.stack(images, conv_pool_drop_2d, zip(filters_counts,
                                                            conv_ksizes,
                                                            conv_strides,
                                                            pool_ksizes,
                                                            pool_strides,
                                                            dropouts[0:conv_layers_count]),
                            scope='conv_layers')

            net = tf.reshape(net, [images.get_shape()[0].value, -1])
            net = slim.stack(net, fc_drop, zip(fc_sizes[:len(fc_sizes) - 1],
                                            dropouts[conv_layers_count:]),
                            scope='fc_layers')

            net = slim.fully_connected(net, fc_sizes[-1], activation_fn=None,
                                    scope='logits')

    return net
