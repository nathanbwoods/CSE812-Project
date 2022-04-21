import math
import random
import matplotlib.pyplot as plt
import numpy as np

num_iterations = 5000

class SensorNetwork:
    """
    Can only read values from nodes, not write them (decentralized network)
    - Know if primary user is active
    - Know what Secondary Users exist, and what they believe/do
    """
    users = [] #devices in the network
    numChannels = 1 #available channels
    data = [] #row 0 = PU, row 1-n = SU; z0 = channel use, z1=belief
    clock = 0

    def __init__(self, userlist, primaryuser):
        self.users = userlist
        self.primaryuser = primaryuser
        self.data = np.zeros(shape = (len(users)+1, num_iterations, 2))

    def update_users(self):
        """
        Advance each Secondary User's clock one step
        :return:
        """
        signal = random.randint(0, 1)
        i = 0
        self.data[i, self.clock, 0] = signal
        
        for user in self.users:
            i += 1
            user.update(self.primary_user_strength(user, signal), self.clock)
            self.data[i, self.clock, 0] = user.get_action()
            self.data[i, self.clock, 1] = user.get_belief()
            
        self.clock += 1
        return signal
        
    def primary_user_strength(self, user, signal):
        distance = math.sqrt((user.x - self.primaryuser.x)**2 + (user.y - self.primaryuser.y)**2)
        noise = (random.random()-0.5)/2
        return signal + noise * distance**2


class User:
    id_value = 0  # this user's id for distinguishability
    channelAllocated = False
    timeSinceAllocation = 0  # elapsed time since this device used a channel
    x = 0 # x position
    y = 0 # y position

    def __init__(self, id_val, x, y):
        self.id_value = id_val
        self.x = x
        self.y = y


class SecondaryUser(User):
    """
    A "good faith" SU, no malicious behavior
    """
    num_users = 0
    trustValue = 0 #user's evaluation of its own trustworthiness, scaled -100 to 100
    users = np.ndarray((num_users,1)) #other users that this device knows of
    trustValues = np.zeros_like(users) #perceived trust values of other users
    primary_user_value = False # belief on whether or not primary user is in the channel
    
    def set_users(self, users):
        self.users = users
    
    def synchronize_trust(self):
        """
        Communicate/receive trust values from other users.
        Ignore broadcast procedures, they can get values from other users at any time.
        :return:
        """
        i = random.randint(1,len(users))
        
        #compare two trust values
        dif = self.users[i].get_trust_value() - self.trustValues[i]
        if dif > 20:
            pass
        i+=1
        
    def broadcast(self):
         """
        broadcast values to all other users
        :return:
        """
    pass
    
    def receive_broadcast(self, trustValues):
         """
        Receive a broadcast of trust values, and adjust own accordingly.
        :return:
        """
    pass
    
    def update(self, primary_user_value, clock, channel_value):
        """
        Decide what actions to take, synchronize trust? Broadcast values? Use channel?
        :return:
        """
        self.clock = clock
        self.primary_user_value = primary_user_value
        x = random.random()
        
        if x < 0.3334: #take channel process
            if primary_user_value == 0 and channel_value == 0:
                if self.trustValue > self.trustValues.max():
                    self.channelAllocated = True
        elif x < 0.6667: # tri-message trust sync
            self.synchronize_trust()
        else: # broadcast
            self.broadcast()
                    
            
    
    def get_action(self):
        """
        :return: boolean true if channel is allocated to this SU
        """
        return self.channelAllocated
    
    def get_belief(self):
        """
        :return: boolean true if channel is believed to be allocated to PU
        """
        return self.primary_user_value
    
    def get_trust_value(self):
        return self.trustValue


class MaliciousUser(SecondaryUser):
    """
    Users with potential to be malicious, some strategy
    """
    pass


def generate_point(mean_x, mean_y, deviation_x, deviation_y):
    return random.gauss(mean_x, deviation_x), random.gauss(mean_y, deviation_y)


def initializeUsers():
    users = []
    # Add 1 primary User
    # Add Secondary Users to network
    cluster_mean_x = 1
    cluster_mean_y = 1
    cluster_deviation_x = 1
    cluster_deviation_y = 1
    point_deviation_x = 0.2
    point_deviation_y = 0.2

    number_of_clusters = 5
    points_per_cluster = 50

    cluster_centers = [generate_point(cluster_mean_x,
                                      cluster_mean_y,
                                      cluster_deviation_x,
                                      cluster_deviation_y)
                       for _ in range(number_of_clusters)]

    points = [generate_point(center_x,
                             center_y,
                             point_deviation_x,
                             point_deviation_y)
              for center_x, center_y in cluster_centers
              for _ in range(points_per_cluster)]

    for i, p in enumerate(points):
        users.append(SecondaryUser(i, p[0], p[1]))
    return users


def plot_users(users, primary_user):
    plt.scatter([user.x for user in users], [user.y for user in users])
    plt.scatter(primary_user.x, primary_user.y, c="red")
    plt.show()


if __name__ == '__main__':
    users = initializeUsers()
    net = SensorNetwork(users, SecondaryUser(-1, 1, 1))
    vals = []
    for i in range(num_iterations):
        net.update_users()
    plot_users(users, SecondaryUser(-1, 1, 1))
