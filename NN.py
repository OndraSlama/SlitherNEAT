import numpy as np
import pickle 

# # X = (hours sleeping, hours studying), y = score on test
# X = np.array(([2, 9], [1, 5], [3, 6]), dtype=float)
# y = np.array(([92], [86], [89]), dtype=float)

# # scale units
# X = X/np.amax(X, axis=0)  # maximum of X array
# y = y/100  # max test score is 100


class NeuralNetwork():
    def __init__(self, inNodes, hiddenNodes = [3], outNodes = 1):
        if isinstance(inNodes, NeuralNetwork):
            net = inNodes            
            # parameters
            self.size = net.size

            # weights  
            self.weights = [] 
            for matrix in net.weights:
                self.weights.append(matrix.copy()) # weight matrix       

            # biases
            self.biases = [] 
            for matrix in net.biases:
                self.biases.append(matrix.copy()) # biases

        else:
            # parameters
            self.size = []
            self.size.append(inNodes)
            for hidden in hiddenNodes:
                self.size.append(hidden)
            self.size.append(outNodes)

            # weights
            self.weights = []
            for i in range(len(self.size)-1):
                self.weights.append(np.random.randn(self.size[i],self.size[i+1]))

            # biases
            self.biases = []
            for i in range(len(self.size)-1):
                self.biases.append(np.random.randn(self.size[i+1]))

    def Forward(self, X_in):

        # save input
        X = np.array(X_in)

        for i in range(len(self.weights)): 
            X = np.dot(X, self.weights[i]) # dot product of X (input) and first set of weights
            X += self.biases[i] # add bias
            X = self.Sigmoid(X) # use activation function        
        
        # save ouput
        Y = X.tolist()
        return Y

    def Copy(self):
        return NeuralNetwork(self)

    def Sigmoid(self, s):
        # activation function
        return 1/(1+np.exp(-s))

    def Mutate(self, rate):
        for i in range(len(self.weights)):
            self.weights[i] = self.MutateMatrix(self.weights[i], rate)

        for i in range(len(self.biases)):
            self.biases[i] = self.MutateMatrix(self.biases[i], rate)
        
    def MutateMatrix(self, matrix, rate):
        shape = matrix.shape                           # Store original shape
        matrix = matrix.flatten()                      # Flatten to 1D
        inds = np.random.choice(matrix.size, size=round(rate*matrix.size))       # Get random indices
        matrix[inds] += np.random.normal(size=matrix[inds].size)/6            
        matrix = matrix.reshape(shape)                                          # Restore original shape
        return matrix

# X = [0.1, 0.2]

# NN = NeuralNetwork(2,[3,2],1)

# NN.Mutate(0.9)

# # defining our output
# o = NN.Forward(X)



# with open('filename_nn.obj', 'wb') as file_nn:
#     pickle.dump(NN, file_nn)

# with open('filename_nn.obj', 'rb') as file_nn2:
#     NN2 = pickle.load(file_nn2)

# # print(NN2)

# print("Predicted Output: \n" + str(o))
# print("Actual Output: \n" + str(y))
