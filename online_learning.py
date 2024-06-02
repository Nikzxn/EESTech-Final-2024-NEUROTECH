from keras.models import Model
from keras.layers import Dense,Input, concatenate
from keras.optimizers import Nadam
from functools import partial
from keras.layers import LeakyReLU



def create_deep_and_wide(units,all_features,num_classes):
    """
        Creates a 'Deep and Wide' neural network model using Keras.

        Args:
            units (int): Number of units in each Dense layer.
            all_features (int): Number of input features.
            num_classes (int): Number of output classes.

        Returns:
            model (keras.models.Model): Compiled Keras model.
    """

    MyDense=partial(Dense,activation=LeakyReLU(0.2),kernel_initializer="he_normal") # wrapper for dense layer

    input =Input((all_features,))
    x=  MyDense(units)(input)
    x = MyDense(units)(x)
    c=concatenate([input,x])
    output=Dense(units=num_classes, activation='softmax')(x )

    model=Model(inputs=[input],outputs=[output])

    optimizer = Nadam(lr=0.0001)
    # Compile the model
    model.compile(loss='sparse_categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    return model
def online_train(model,X,y):
    """
       Performs online training on the model using a single batch of data.

       Args:
           model (keras.models.Model): Keras model to train.
           X (numpy.ndarray): Input features for training.
           y (numpy.ndarray): Labels for training.
    """
    model.train_on_batch(X,y)

# receives action of the user and state of the env.
def receive_new_data():
    """
       Placeholder function to simulate receiving new data.
       This function should be replaced with actual data receiving logic.

       Returns:
           tuple: A tuple (X_new, y_new) representing new input data and labels.
    """
    pass


def run():
    """
        Main function to initialize and run the online learning loop.
    """
    stations = 1
    features = 4
    all_features = features * stations
    num_classes = 4

    model=create_deep_and_wide(all_features,num_classes)
    print(model.summary())


    score=0
    factor=0.8

   # Online learning loop
    while True:
        # Receive new data instance
        X_new, y_new = receive_new_data()

        pred=model.predict(X_new,verbose=None).argmax(axis=1)


        score=factor*score+(1-factor)*(pred==y_new)#computes score with factor of previous one

        print(score,X_new,y_new)

        online_train(model, X_new, y_new)

        model.save('online_learning_model.h5')