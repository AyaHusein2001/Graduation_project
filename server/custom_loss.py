# custom_loss.py

import tensorflow as tf
from tensorflow.keras import backend as K

def focal_loss(alpha=None, gamma=2.0):
    def focal_loss_fixed(y_true, y_pred):
        y_pred = K.clip(y_pred, K.epsilon(), 1.0 - K.epsilon())
        cross_entropy = -y_true * K.log(y_pred)

        if alpha is not None:
            alpha_tensor = tf.constant(alpha, dtype=tf.float32)
            alpha_factor = y_true * alpha_tensor + (1 - y_true) * (1 - alpha_tensor)
            focal_weight = alpha_factor * K.pow(1 - y_pred, gamma)
        else:
            focal_weight = K.pow(1 - y_pred, gamma)

        loss = focal_weight * cross_entropy
        return K.sum(loss, axis=-1)

    return focal_loss_fixed

def custom_loss_(y_true, y_pred):
    # Define penalties (higher penalty for misclassifying label 1 and label 2)
    penalty = tf.constant([1.0, 5.0,5.0,2.0, 5.0])  # Adjust penalties as needed

    # Compute loss using categorical crossentropy
    loss = tf.keras.losses.categorical_crossentropy(y_true, y_pred)

    # Apply penalties based on true labels
    weighted_loss = tf.multiply(loss, tf.gather(penalty, tf.argmax(y_true, axis=-1)))

    return weighted_loss
