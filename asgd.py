from pylearn2.training_algorithms.training_algorithm import TrainingAlgorithm





class ASGD(pylearn2.train_TrainingAlgorithm):
	"""
	ASGD = (Minibatch) Asynchronous Distributed Stochastic Gradient Descent.

	Parameters
	----------
	learning_rate : float
        The learning rate to use. Train object callbacks can change the
        learning rate after each epoch. SGD update_callbacks can change
        it after each minibatch.

    cost : pylearn2.costs.cost.Cost, optional
        Cost object specifying the objective function to be minimized.
        Optionally, may be None. In this case, SGD will call the model's
        get_default_cost method to obtain the objective function.

    batch_size : int, optional
        The size of the batch to be used.
        If not specified, the model will be asked for the batch size, so
        you must have specified the batch size there.
        (Some models are rigidly defined to only work with one batch size)        

    n_push : int, optional
    	How often to push gradients from cores to parameter servers. The default
    	behavior is that gradients as soon as they become available.

    n_pull : int, optional
    	How often to pull gradients from parameter servers to cores. The default
    	behavior is that parameters are updated after each push.

	"""
	def __init__(self, learning_rate, cost=None, batch_size=None, n_push=1,
			     n_pull=1):
		self.learning_rate = learning_rate
		self.cost = cost
		self.batch_size = batch_size
		self.n_push = n_push
		self.n_pull = n_pull

	def setup(self, model, dataset):
		"""
		Spawn n_parameter_servers