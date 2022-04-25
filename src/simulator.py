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


import random


class User:
    clock = 0  # Keeps track of the logical time for a device
    id_value = 0  # This user's id for distinguishability
    channelAllocated = False  # Boolean, is a the channel allocated for this device
    timeSinceAllocation = 0  # The elapsed time since this device used a channel
    num_users = 0  # The total number of users in our network
    # user_ids = [] # List containing all instances (ids) of Users in our network
    user_list = []

    def __init__(self, id_val):
        self.id_value = id_val

        User.num_users += 1  # Update the number of users everytime a new user is created
        # User.user_ids.append(self.id) # Append the new user id to a list shared between all user instances
        User.user_list.append(self)

    # every user broadcasts their belief
    # the one that's incongruent with the others is likely the MU
    # that device has its CTV decremented by -15


class SecondaryUser(User):
    """
    A "good faith" SU, no malicious behavior
    """
    trust_value = 0  # The user's evaluation of its own trustworthiness, scaled -100 to 100
    all_trust_values = [0 * (len(User.user_list))]  # The perceived trust values of other users
    primary_user_value = False  # The belief on whether or not primary user is in the channel

    def set_users(self, users):
        self.user_list = User.user_list

    def synchronize_trust(self):
        """
        Communicate/receive trust values from other users.
        Ignore broadcast procedures, they can get values from other users at any time.
        :return:
        """
        beliefs = []

        for i in range(len(self.user_list)):
            # Iterate through the list of all users, get their belief
            # of if the PU is present
            # get_belief returns a bool, which we convert to an int
            beliefs.append(int(self.user_list[i].get_belief()))

        # if this is true then all nodes are reporting that
        # the PU is present except for 1 - the MU
        if sum(beliefs) == len(self.user_list) - 1:
            MU_index = beliefs.index(0)
            self.user_list[MU_index].trust_value = self.user_list[MU_index].trust_value - 15

        # if this is true all users are reporting that
        # the PU is NOT present except for 1 - the MU
        elif sum(beliefs) == 1:
            MU_index = beliefs.index(1)
            self.user_list[MU_index].trust_value = self.user_list[MU_index].trust_value - 15

        else:
            # as there has been no detection of an SSDF attack by either devices
            # the nodes are rewarded by having their trust values incremented by 5
            mean = (self.user_list[i].get_trust_values() + self.all_trust_values) // 2
            self.user_list[i].trust_value = mean + 5
            self.trust_value = mean + 5

    def receive_broadcast(self, trustValues, trust_value_other_device):
        """
        Recieve a broadcast of trust values from another device and update
        the instance's trust values accordingly
        """
        # compare the nodes trust values and use that as a weight to update the trust
        # values of the device
        sum_of_trust_values = self.trust_value + trust_value_other_device
        ratio = trust_value_other_device / sum_of_trust_values
        self.all_trust_values = self.all_trust_values + (ratio) * trustValues

    def broadcast(self):
        """
        Broadcast values to all other users
        """
        # For all users in the network, make them recieve
        # the trust values of this particular instance
        for i in range(len(self.user_list)):
            self.user_list[i].recieve_broadcast(self.all_trust_values)

    def update(self, primary_user_value, clock, channel_value):
        """
        Decide what actions to take, synchronize trust? Broadcast values? Use channel?
        :return:
        """
        self.clock = clock
        self.primary_user_value = primary_user_value
        x = random.random()

        if x < 0.3334:  # take channel process
            if primary_user_value == 0 and channel_value == 0:
                if self.trust_value == max(self.all_trust_values):  # highest in network
                    self.channelAllocated = True
        elif x < 0.6667:  # tri-message trust sync
            self.synchronize_trust()
        else:  # broadcast
            self.broadcast()

        def get_action(self):
            """:
            return: boolean true if channel is allocated to this SU
            """
            return self.channel_allocated

        def get_belief(self):
            """
            :return: boolean true if channel is believed to be allocated to PU
            """
            return User.primary_user_value

        def get_trust_value(self):
            """
            :return: int the trust value
            """
            return self.trust_value


class MaliciousUser(SecondaryUser):
    """
    Users with potential to be malicious, some strategy:
    -Selfish SSDF: Falsely report that PU is present, in order to gain exclusive access to the desired
    spectrum.
    - Interference SSDF: Falsely report that PU is not present, in order to cause interference to PU.
    - Confusing SSDF: Randomly reports a true or false value for primary user energy, preventing a
    consensus.
    """

    def SelfishSSDF(self):
        if not self.get_belief():
            self.primary_user_value = True

    def InterferenceSSDF(self):
        if self.get_belief():
            self.primary_user_value = False

    def ConfusingSSDF(self):
        z = random.random()
        if z < 0.5:
            self.primary_user_value = True
        else:
            self.primary_user_value = False


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
        users.append(SecondaryUser(i))
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
