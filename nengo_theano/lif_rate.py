from _collections import OrderedDict

import theano
from theano import tensor as TT

import neuron


class LIFRateNeuron(neuron.Neuron):
    def __init__(self, size, tau_rc=0.02, tau_ref=0.002):
        """Constructor for a set of LIF rate neuron

        :param int size: number of neurons in set
        :param float t_rc: the RC time constant
        :param float tau_ref: refractory period length (s)

        """
        neuron.Neuron.__init__(self, size)
        self.tau_rc = tau_rc
        self.tau_ref = tau_ref

    def make_alpha_bias(self, max_rates, intercepts):
        """Compute the alpha and bias needed to get the given max_rate
        and intercept values.
        
        Returns gain (alpha) and offset (j_bias) values of neurons.

        :param float array max_rates: maximum firing rates of neurons
        :param float array intercepts: x-intercepts of neurons
        
        """
        x = 1.0 / (1 - TT.exp(
                (self.tau_ref - (1.0 / max_rates)) / self.tau_rc))
        alpha = (1 - z2) / (intercepts - 1.0)
        j_bias = 1 - alpha * intercepts
        return alpha, j_bias

    def update(self, J, dt):
        """Theano update rule that implementing LIF rate neuron type.
        
        Returns dictionary with firing rate for current time step.

        :param float array J:
            the input current for the current time step
        
        """
        # set up denominator of LIF firing rate equation
        rate = self.tau_ref - self.tau_rc * TT.log(
            1 - 1.0 / TT.maximum(J, 0))
        
        # if input current is enough to make neuron spike,
        # calculate firing rate, else return 0
        rate = TT.switch(J > 1, 1 / rate, 0)

        # return dictionary of internal variables to update
        return OrderedDict({
                self.output: TT.unbroadcast(rate.astype('float32'), 0)
                })

neuron.types['lif-rate'] = LIFRateNeuron

