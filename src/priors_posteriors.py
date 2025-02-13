import tensorflow as tf
import tf_keras as tfk
import tensorflow_probability as tfp


def std_normal_prior(kernel_size: int, bias_size: int, dtype=None) -> callable:
    n = kernel_size + bias_size
    prior_model = tfk.Sequential(
        [
            tfp.layers.DistributionLambda(
                lambda t: tfp.distributions.MultivariateNormalDiag(
                    loc=tf.zeros(n), scale_diag=tf.ones(n)
                )
            )
        ],
        name="prior_seq",
    )
    return prior_model


def std_normal_posterior(
    kernel_size: int, bias_size: int, dtype=None
) -> callable:
    n = kernel_size + bias_size
    posterior_model = tfk.Sequential(
        [
            tfp.layers.VariableLayer(
                tfp.layers.MultivariateNormalTriL.params_size(n), dtype=dtype
            ),
            tfp.layers.MultivariateNormalTriL(n),
        ],
        name="posterior_seq",
    )
    return posterior_model
